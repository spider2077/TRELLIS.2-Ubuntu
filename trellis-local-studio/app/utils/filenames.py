"""Filename helpers for local input and output folders."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path


def safe_slug(value: str, fallback: str = "job") -> str:
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "-", value.strip()).strip("-._").lower()
    return slug[:80] or fallback


def timestamp_slug() -> str:
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def unique_job_dir(output_root: Path, job_name: str) -> Path:
    base = output_root / f"{timestamp_slug()}_{safe_slug(job_name)}"
    candidate = base
    suffix = 1
    while candidate.exists():
        suffix += 1
        candidate = Path(f"{base}-{suffix}")
    candidate.mkdir(parents=True, exist_ok=False)
    return candidate


def safe_upload_name(filename: str, fallback: str = "input") -> str:
    path = Path(filename or fallback)
    stem = safe_slug(path.stem, fallback)
    suffix = path.suffix.lower()
    return f"{stem}{suffix}"

