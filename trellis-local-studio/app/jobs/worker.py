"""Sequential background worker for TRELLIS generation jobs."""

from __future__ import annotations

import asyncio
import json
from datetime import datetime
from typing import Any

from app.config import APP_NAME, settings
from app.engine.export_options import ExportOptions
from app.engine.gpu_guard import GPUGuard
from app.engine.trellis_engine import TrellisEngine
from app.jobs.job_store import JobStore
from app.utils.system_info import nvidia_smi_info


class JobWorker:
    def __init__(self, store: JobStore, engine: TrellisEngine, gpu_guard: GPUGuard) -> None:
        self.store = store
        self.engine = engine
        self.gpu_guard = gpu_guard
        self.queue: asyncio.Queue[str] = asyncio.Queue()
        self._task: asyncio.Task[None] | None = None

    def start(self) -> None:
        if self._task is None:
            self._task = asyncio.create_task(self._loop())

    async def enqueue(self, job_id: str) -> None:
        await self.queue.put(job_id)

    def queue_size(self) -> int:
        return self.queue.qsize()

    async def _loop(self) -> None:
        while True:
            job_id = await self.queue.get()
            try:
                await self._process(job_id)
            finally:
                self.queue.task_done()

    async def _process(self, job_id: str) -> None:
        async with self.gpu_guard:
            await asyncio.to_thread(self._run_job_sync, job_id)

    def _run_job_sync(self, job_id: str) -> None:
        job = self.store.get(job_id)
        if job is None:
            return

        def log(message: str) -> None:
            self.store.append_log(job_id, message)

        options = ExportOptions(**job.settings)
        try:
            self.store.update(
                job_id,
                status="loading_model",
                progress=10,
                started_at=datetime.now().isoformat(timespec="seconds"),
            )
            self.gpu_guard.write_snapshot("before job", job.log_path)
            metadata = self._metadata(job_id)

            self.store.update(job_id, status="running", progress=35)
            outputs = self.engine.generate(job.normalized_image, job.job_dir, options, metadata, log)

            self.store.update(job_id, status="completed", progress=100)
            self.gpu_guard.write_snapshot("after job", job.log_path)
            self.store.update(
                job_id,
                glb_path=outputs.glb,
                preview_path=outputs.preview,
                metadata_path=outputs.metadata,
                completed_at=datetime.now().isoformat(timespec="seconds"),
            )
            log("Job completed.")
        except Exception as exc:
            self.store.update(
                job_id,
                status="failed",
                progress=100,
                error=str(exc),
                completed_at=datetime.now().isoformat(timespec="seconds"),
            )
            log(f"Job failed: {exc}")
            metadata = self._metadata(job_id)
            metadata["error"] = str(exc)
            (job.job_dir / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    def _metadata(self, job_id: str) -> dict[str, Any]:
        job = self.store.get(job_id)
        assert job is not None
        return {
            "app_name": APP_NAME,
            "model": settings.model_name,
            "job_id": job.id,
            "job_name": job.name,
            "mode": job.mode,
            "input_file": job.normalized_image.name,
            "created_at": job.created_at,
            "gpu": nvidia_smi_info(),
            "settings": job.settings,
            "front_back_note": (
                "TRELLIS.2 generation is single-image based. Front/back mode stores both "
                "images and generates from the selected primary image only."
                if job.mode == "front_back"
                else None
            ),
            "outputs": {"glb": None, "preview": None},
        }

