"""System and GPU inspection helpers."""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


def _run(command: list[str]) -> tuple[int, str, str]:
    try:
        completed = subprocess.run(command, check=False, capture_output=True, text=True, timeout=10)
        return completed.returncode, completed.stdout.strip(), completed.stderr.strip()
    except FileNotFoundError:
        return 127, "", f"{command[0]} not found"
    except subprocess.TimeoutExpired:
        return 124, "", f"{command[0]} timed out"


def nvidia_smi_info() -> dict[str, Any]:
    query = [
        "nvidia-smi",
        "--query-gpu=name,driver_version,memory.total,memory.free,memory.used",
        "--format=csv,noheader,nounits",
    ]
    code, stdout, stderr = _run(query)
    if code != 0 or not stdout:
        return {"available": False, "error": stderr or "nvidia-smi returned no GPU data"}

    first_gpu = stdout.splitlines()[0]
    parts = [part.strip() for part in first_gpu.split(",")]
    if len(parts) < 5:
        return {"available": False, "error": f"Unexpected nvidia-smi output: {first_gpu}"}

    total_mb = int(float(parts[2]))
    free_mb = int(float(parts[3]))
    used_mb = int(float(parts[4]))
    return {
        "available": True,
        "name": parts[0],
        "driver_version": parts[1],
        "vram_total_mb": total_mb,
        "vram_free_mb": free_mb,
        "vram_used_mb": used_mb,
        "vram_total_gb": round(total_mb / 1024, 2),
        "vram_free_gb": round(free_mb / 1024, 2),
        "below_24gb_warning": total_mb < 24 * 1024,
    }


def torch_info() -> dict[str, Any]:
    try:
        import torch
    except Exception as exc:  # pragma: no cover - depends on local environment
        return {"installed": False, "error": str(exc)}

    info: dict[str, Any] = {
        "installed": True,
        "version": getattr(torch, "__version__", "unknown"),
        "cuda_available": torch.cuda.is_available(),
    }
    if torch.cuda.is_available():
        info["cuda_device"] = torch.cuda.get_device_name(0)
        info["cuda_version"] = getattr(torch.version, "cuda", None)
        info["device_total_vram_gb"] = round(
            torch.cuda.get_device_properties(0).total_memory / 1024**3,
            2,
        )
    return info


def disk_info(path: Path) -> dict[str, Any]:
    usage = shutil.disk_usage(path)
    return {
        "path": str(path),
        "total_gb": round(usage.total / 1024**3, 2),
        "free_gb": round(usage.free / 1024**3, 2),
        "used_gb": round(usage.used / 1024**3, 2),
    }


def collect_system_info(output_dir: Path, app_host: str) -> dict[str, Any]:
    return {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "cuda_home": os.environ.get("CUDA_HOME"),
        "conda_env": os.environ.get("CONDA_DEFAULT_ENV"),
        "host": app_host,
        "local_only": app_host in {"127.0.0.1", "localhost"},
        "nvidia_smi": nvidia_smi_info(),
        "torch": torch_info(),
        "disk": disk_info(output_dir),
    }

