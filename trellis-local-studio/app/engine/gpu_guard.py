"""Single-GPU guard for RTX 3090-friendly job execution."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from app.utils.system_info import nvidia_smi_info


class GPUGuard:
    """Serialize TRELLIS jobs unless unsafe parallel mode is explicitly enabled."""

    def __init__(self, unsafe_parallel_jobs: bool = False) -> None:
        self._unsafe_parallel_jobs = unsafe_parallel_jobs
        self._lock = asyncio.Lock()

    async def __aenter__(self) -> "GPUGuard":
        if not self._unsafe_parallel_jobs:
            await self._lock.acquire()
        return self

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None:
        if not self._unsafe_parallel_jobs and self._lock.locked():
            self._lock.release()

    def snapshot(self) -> dict[str, Any]:
        return nvidia_smi_info()

    def write_snapshot(self, label: str, log_path: Path) -> None:
        info = self.snapshot()
        with log_path.open("a", encoding="utf-8") as log_file:
            log_file.write(f"[gpu] {label}: {info}\n")

