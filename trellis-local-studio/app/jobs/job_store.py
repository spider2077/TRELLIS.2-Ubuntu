"""In-memory job store with on-disk job artifacts."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.engine.export_options import ExportOptions


TERMINAL_STATUSES = {"completed", "failed", "cancelled"}


@dataclass
class Job:
    id: str
    name: str
    mode: str
    preset: str
    status: str
    progress: int
    created_at: str
    job_dir: Path
    primary_image: Path
    normalized_image: Path
    log_path: Path
    settings: dict[str, Any]
    front_image: Path | None = None
    back_image: Path | None = None
    glb_path: Path | None = None
    preview_path: Path | None = None
    metadata_path: Path | None = None
    error: str | None = None
    started_at: str | None = None
    completed_at: str | None = None
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        for key in (
            "job_dir",
            "primary_image",
            "normalized_image",
            "log_path",
            "front_image",
            "back_image",
            "glb_path",
            "preview_path",
            "metadata_path",
        ):
            if payload[key] is not None:
                payload[key] = str(payload[key])
        payload["download"] = {
            "glb": f"/api/jobs/{self.id}/download/glb" if self.glb_path else None,
            "preview": f"/api/jobs/{self.id}/download/preview" if self.preview_path else None,
            "log": f"/api/jobs/{self.id}/log",
            "metadata": f"/api/jobs/{self.id}/download/metadata" if self.metadata_path else None,
        }
        return payload


class JobStore:
    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}

    def create(
        self,
        *,
        name: str,
        mode: str,
        job_dir: Path,
        primary_image: Path,
        normalized_image: Path,
        options: ExportOptions,
        front_image: Path | None = None,
        back_image: Path | None = None,
        warnings: list[str] | None = None,
    ) -> Job:
        job = Job(
            id=uuid4().hex,
            name=name,
            mode=mode,
            preset=options.preset,
            status="queued",
            progress=0,
            created_at=datetime.now().isoformat(timespec="seconds"),
            job_dir=job_dir,
            primary_image=primary_image,
            normalized_image=normalized_image,
            log_path=job_dir / "job.log",
            settings=options.to_dict(),
            front_image=front_image,
            back_image=back_image,
            warnings=warnings or [],
        )
        self._jobs[job.id] = job
        self.append_log(job.id, f"Created job {job.id} ({job.name}).")
        return job

    def list(self) -> list[Job]:
        return sorted(self._jobs.values(), key=lambda job: job.created_at, reverse=True)

    def get(self, job_id: str) -> Job | None:
        return self._jobs.get(job_id)

    def update(self, job_id: str, **fields: Any) -> Job:
        job = self._jobs[job_id]
        for key, value in fields.items():
            setattr(job, key, value)
        return job

    def append_log(self, job_id: str, message: str) -> None:
        job = self._jobs[job_id]
        timestamp = datetime.now().isoformat(timespec="seconds")
        job.log_path.parent.mkdir(parents=True, exist_ok=True)
        with job.log_path.open("a", encoding="utf-8") as log_file:
            log_file.write(f"[{timestamp}] {message}\n")

