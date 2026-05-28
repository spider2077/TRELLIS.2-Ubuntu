"""FastAPI backend for Trellis Local Studio."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles

from app.config import APP_NAME, WEB_DIR, ensure_directories, settings
from app.engine.export_options import build_export_options, options_payload
from app.engine.gpu_guard import GPUGuard
from app.engine.trellis_engine import TrellisEngine
from app.jobs.job_store import JobStore
from app.jobs.worker import JobWorker
from app.utils.filenames import safe_slug, safe_upload_name, unique_job_dir
from app.utils.image_prep import InvalidImageError, normalize_image
from app.utils.system_info import collect_system_info


ensure_directories()

app = FastAPI(title=APP_NAME)
app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")

store = JobStore()
engine = TrellisEngine(model_name=settings.model_name)
gpu_guard = GPUGuard(unsafe_parallel_jobs=settings.unsafe_parallel_jobs)
worker = JobWorker(store=store, engine=engine, gpu_guard=gpu_guard)


@app.on_event("startup")
async def startup() -> None:
    worker.start()


@app.get("/")
async def index() -> FileResponse:
    return FileResponse(WEB_DIR / "index.html")


@app.get("/api/health")
async def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "app_name": APP_NAME,
        "local_only": settings.local_only,
        "host": settings.host,
        "image_to_3d_only": True,
        "no_text_to_image": True,
        "model": engine.status(),
        "queued_jobs": worker.queue_size(),
    }


@app.get("/api/system")
async def system() -> dict[str, Any]:
    return collect_system_info(settings.output_dir, settings.host)


@app.get("/api/options")
async def options() -> dict[str, Any]:
    return options_payload()


@app.get("/api/model/status")
async def model_status() -> dict[str, Any]:
    return engine.status()


@app.post("/api/model/preload")
async def preload_model() -> dict[str, Any]:
    try:
        await _run_blocking(engine.load)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return engine.status()


@app.post("/api/model/unload")
async def unload_model() -> dict[str, Any]:
    engine.unload()
    return engine.status()


@app.post("/api/cache/clear")
async def clear_cache() -> dict[str, Any]:
    try:
        import torch

        torch.cuda.empty_cache()
        return {"status": "cleared"}
    except Exception as exc:
        return {"status": "skipped", "detail": str(exc)}


@app.post("/api/jobs")
async def create_job(
    image: UploadFile = File(...),
    back_image: UploadFile | None = File(None),
    mode: str = Form("single"),
    primary_image: str = Form("front"),
    preset: str = Form("balanced"),
    output_basename: str | None = Form(None),
    decimation_target: int | None = Form(None),
    texture_size: int | None = Form(None),
    remesh: str | None = Form(None),
    remesh_band: int | None = Form(None),
    remesh_project: float | None = Form(None),
    extension_webp: str | None = Form(None),
    render_preview: str | None = Form(None),
    preview_fps: int | None = Form(None),
    preview_turntable_seconds: int | None = Form(None),
) -> dict[str, Any]:
    mode_key = mode.strip().lower()
    if mode_key not in {"single", "front_back", "batch"}:
        raise HTTPException(status_code=400, detail="Unsupported mode.")
    if mode_key == "front_back" and primary_image not in {"front", "back"}:
        raise HTTPException(status_code=400, detail="primary_image must be front or back.")

    job_name = safe_slug(output_basename or Path(image.filename or "job").stem, "job")
    job_dir = unique_job_dir(settings.output_dir, job_name)
    try:
        front_path = _save_upload(image, job_dir, "input_front_original" if mode_key == "front_back" else "input_original")
        back_path = _save_upload(back_image, job_dir, "input_back_original") if back_image else None
        if mode_key == "front_back" and primary_image == "back":
            if back_path is None:
                raise HTTPException(status_code=400, detail="Back image is required when primary image is back.")
            primary_path = back_path
        else:
            primary_path = front_path

        normalized_path = job_dir / "input_normalized.png"
        image_info = normalize_image(primary_path, normalized_path)
        options = build_export_options(
            preset=preset,
            output_basename=job_name,
            decimation_target=decimation_target,
            texture_size=texture_size,
            remesh=remesh,
            remesh_band=remesh_band,
            remesh_project=remesh_project,
            extension_webp=extension_webp,
            render_preview=render_preview,
            preview_fps=preview_fps,
            preview_turntable_seconds=preview_turntable_seconds,
        )
    except HTTPException:
        shutil.rmtree(job_dir, ignore_errors=True)
        raise
    except InvalidImageError as exc:
        shutil.rmtree(job_dir, ignore_errors=True)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except ValueError as exc:
        shutil.rmtree(job_dir, ignore_errors=True)
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    warnings = _settings_warnings(options.to_dict(), mode_key)
    job = store.create(
        name=job_name,
        mode=mode_key,
        job_dir=job_dir,
        primary_image=primary_path,
        normalized_image=normalized_path,
        options=options,
        front_image=front_path if mode_key == "front_back" else None,
        back_image=back_path,
        warnings=warnings,
    )
    store.append_log(job.id, f"Normalized image info: {image_info}")
    await worker.enqueue(job.id)
    return {"job": job.to_dict(), "queue_size": worker.queue_size()}


@app.get("/api/jobs")
async def list_jobs() -> dict[str, Any]:
    return {"jobs": [job.to_dict() for job in store.list()], "queue_size": worker.queue_size()}


@app.get("/api/jobs/{job_id}")
async def get_job(job_id: str) -> dict[str, Any]:
    job = _require_job(job_id)
    return {"job": job.to_dict()}


@app.get("/api/jobs/{job_id}/download/glb")
async def download_glb(job_id: str) -> FileResponse:
    job = _require_job(job_id)
    return _download(job.glb_path, "GLB is not ready for this job.")


@app.get("/api/jobs/{job_id}/download/preview")
async def download_preview(job_id: str) -> FileResponse:
    job = _require_job(job_id)
    return _download(job.preview_path, "Preview is not available for this job.")


@app.get("/api/jobs/{job_id}/download/metadata")
async def download_metadata(job_id: str) -> FileResponse:
    job = _require_job(job_id)
    metadata_path = job.metadata_path or job.job_dir / "metadata.json"
    return _download(metadata_path, "Metadata is not ready for this job.")


@app.get("/api/jobs/{job_id}/log")
async def get_log(job_id: str) -> PlainTextResponse:
    job = _require_job(job_id)
    if not job.log_path.exists():
        return PlainTextResponse("", media_type="text/plain")
    return PlainTextResponse(job.log_path.read_text(encoding="utf-8"), media_type="text/plain")


def _require_job(job_id: str):
    job = store.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found.")
    return job


def _download(path: Path | None, missing_message: str) -> FileResponse:
    if path is None or not path.exists():
        raise HTTPException(status_code=404, detail=missing_message)
    return FileResponse(path)


def _save_upload(upload: UploadFile | None, job_dir: Path, basename: str) -> Path:
    if upload is None:
        raise HTTPException(status_code=400, detail="Missing upload.")
    filename = safe_upload_name(upload.filename or basename)
    suffix = Path(filename).suffix.lower()
    destination = job_dir / f"{basename}{suffix}"
    with destination.open("wb") as output_file:
        shutil.copyfileobj(upload.file, output_file)
    return destination


def _settings_warnings(options: dict[str, Any], mode: str) -> list[str]:
    warnings: list[str] = []
    if not settings.local_only:
        warnings.append("LAN mode is enabled. Local-only mode is recommended by default.")
    if options["texture_size"] == 8192 or options["decimation_target"] >= 4_000_000:
        warnings.append("8192 textures and very high decimation targets may exceed RTX 3090 VRAM.")
    if mode == "front_back":
        warnings.append(
            "Front/back mode is organizational. TRELLIS.2 generates from the selected primary image only."
        )
    return warnings


async def _run_blocking(func):
    import asyncio

    return await asyncio.to_thread(func)

