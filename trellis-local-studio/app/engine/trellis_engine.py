"""Lazy TRELLIS.2 engine wrapper used by the local app."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from PIL import Image

from app.config import DEFAULT_MODEL, REPO_ROOT
from app.engine.export_options import ExportOptions


LogFn = Callable[[str], None]


@dataclass(frozen=True)
class GenerationOutputs:
    glb: Path
    preview: Path | None
    metadata: Path


class TrellisEngine:
    """Owns the official TRELLIS.2 pipeline and hides model details from the UI."""

    def __init__(self, model_name: str = DEFAULT_MODEL) -> None:
        self.model_name = model_name
        self.pipeline: Any | None = None
        self.loaded_at: float | None = None

    @property
    def is_loaded(self) -> bool:
        return self.pipeline is not None

    def status(self) -> dict[str, Any]:
        return {
            "model": self.model_name,
            "loaded": self.is_loaded,
            "loaded_at": self.loaded_at,
        }

    def load(self, log: LogFn | None = None) -> None:
        if self.pipeline is not None:
            return
        if log:
            log(f"Loading TRELLIS.2 model: {self.model_name}")
        from trellis2.pipelines import Trellis2ImageTo3DPipeline

        self.pipeline = Trellis2ImageTo3DPipeline.from_pretrained(self.model_name)
        self.pipeline.cuda()
        self.loaded_at = time.time()
        if log:
            log("TRELLIS.2 model loaded on CUDA.")

    def unload(self, log: LogFn | None = None) -> None:
        self.pipeline = None
        self.loaded_at = None
        try:
            import torch

            torch.cuda.empty_cache()
        except Exception:
            pass
        if log:
            log("TRELLIS.2 model unloaded and CUDA cache cleared.")

    def generate(
        self,
        image_path: Path,
        job_dir: Path,
        options: ExportOptions,
        metadata: dict[str, Any],
        log: LogFn,
    ) -> GenerationOutputs:
        """Run single-image TRELLIS.2 generation and export a GLB."""

        started = time.time()
        try:
            self.load(log)
            assert self.pipeline is not None

            log(f"Opening normalized image: {image_path}")
            image = Image.open(image_path)

            log("Running TRELLIS.2 image-to-3D generation.")
            mesh = self.pipeline.run(image)[0]
            if hasattr(mesh, "simplify"):
                mesh.simplify(16_777_216)  # nvdiffrast face-count limit from official examples.

            glb_path = job_dir / f"{options.output_basename}.glb"
            log(f"Exporting GLB: {glb_path}")
            glb = self._to_glb(mesh, options)
            glb.export(str(glb_path), extension_webp=options.extension_webp)

            preview_path = None
            if options.render_preview:
                preview_path = job_dir / "preview.mp4"
                self._render_preview(mesh, preview_path, options, log)

            metadata["outputs"] = {
                "glb": glb_path.name,
                "preview": preview_path.name if preview_path else None,
            }
            metadata["durations"] = {"total_seconds": round(time.time() - started, 3)}
            metadata_path = job_dir / "metadata.json"
            metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
            self._empty_cuda_cache(log)
            return GenerationOutputs(glb=glb_path, preview=preview_path, metadata=metadata_path)
        except Exception as exc:
            self._empty_cuda_cache(log)
            raise self._friendly_error(exc) from exc

    def _to_glb(self, mesh: Any, options: ExportOptions) -> Any:
        import o_voxel

        return o_voxel.postprocess.to_glb(
            vertices=mesh.vertices,
            faces=mesh.faces,
            attr_volume=mesh.attrs,
            coords=mesh.coords,
            attr_layout=mesh.layout,
            voxel_size=mesh.voxel_size,
            aabb=[[-0.5, -0.5, -0.5], [0.5, 0.5, 0.5]],
            decimation_target=options.decimation_target,
            texture_size=options.texture_size,
            remesh=options.remesh,
            remesh_band=options.remesh_band,
            remesh_project=options.remesh_project,
            verbose=True,
        )

    def _render_preview(self, mesh: Any, preview_path: Path, options: ExportOptions, log: LogFn) -> None:
        try:
            import cv2
            import imageio
            import torch
            from trellis2.renderers import EnvMap
            from trellis2.utils import render_utils

            log(f"Rendering preview video: {preview_path}")
            envmap = EnvMap(
                torch.tensor(
                    cv2.cvtColor(
                        cv2.imread(str(REPO_ROOT / "assets" / "hdri" / "forest.exr"), cv2.IMREAD_UNCHANGED),
                        cv2.COLOR_BGR2RGB,
                    ),
                    dtype=torch.float32,
                    device="cuda",
                )
            )
            frames = render_utils.make_pbr_vis_frames(render_utils.render_video(mesh, envmap=envmap))
            imageio.mimsave(str(preview_path), frames, fps=options.preview_fps)
        except Exception as exc:
            log(f"Preview render failed; continuing with GLB output. Error: {exc}")

    def _empty_cuda_cache(self, log: LogFn) -> None:
        try:
            import torch

            torch.cuda.empty_cache()
            log("CUDA cache cleared.")
        except Exception:
            log("CUDA cache clear skipped; PyTorch CUDA is not available.")

    def _friendly_error(self, exc: Exception) -> RuntimeError:
        message = str(exc)
        if "out of memory" in message.lower() or "cuda oom" in message.lower():
            return RuntimeError(
                "CUDA out of memory. Use Draft or Balanced, lower texture size or "
                "decimation target, close other GPU apps, then restart the app if needed."
            )
        return RuntimeError(message)

