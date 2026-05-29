"""Runtime configuration for Trellis Local Studio."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path


# These must be set before importing OpenCV, PyTorch, or TRELLIS.2 internals.
os.environ.setdefault("OPENCV_IO_ENABLE_OPENEXR", "1")
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")


APP_NAME = "Trellis Local Studio"
DEFAULT_MODEL = "microsoft/TRELLIS.2-4B"

APP_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = APP_ROOT.parent

_repo_root_str = str(REPO_ROOT)
if _repo_root_str not in sys.path:
    sys.path.insert(0, _repo_root_str)
INPUT_DIR = APP_ROOT / "input"
OUTPUT_DIR = APP_ROOT / "output"
CACHE_DIR = APP_ROOT / "cache"
LOG_DIR = APP_ROOT / "logs"
WEB_DIR = APP_ROOT / "app" / "web"
CONFIG_PATH = APP_ROOT / "config.local.json"


@dataclass(frozen=True)
class Settings:
    """Environment-backed settings with safe local defaults."""

    host: str = os.environ.get("TRELLIS_LOCAL_HOST", "127.0.0.1")
    port: int = int(os.environ.get("TRELLIS_LOCAL_PORT", "7860"))
    model_name: str = os.environ.get("TRELLIS_MODEL_NAME", DEFAULT_MODEL)
    output_dir: Path = Path(os.environ.get("TRELLIS_OUTPUT_DIR", str(OUTPUT_DIR)))
    input_dir: Path = Path(os.environ.get("TRELLIS_INPUT_DIR", str(INPUT_DIR)))
    cache_dir: Path = Path(os.environ.get("TRELLIS_CACHE_DIR", str(CACHE_DIR)))
    log_dir: Path = Path(os.environ.get("TRELLIS_LOG_DIR", str(LOG_DIR)))
    unsafe_parallel_jobs: bool = os.environ.get("TRELLIS_UNSAFE_PARALLEL_JOBS", "0") == "1"

    @property
    def local_only(self) -> bool:
        return self.host in {"127.0.0.1", "localhost"}


settings = Settings()


def ensure_directories() -> None:
    """Create local runtime directories used by the app."""

    for path in (settings.input_dir, settings.output_dir, settings.cache_dir, settings.log_dir):
        path.mkdir(parents=True, exist_ok=True)

