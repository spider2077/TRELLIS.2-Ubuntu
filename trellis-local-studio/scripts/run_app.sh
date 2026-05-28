#!/usr/bin/env bash
# Script: run_app.sh
# Location: trellis-local-studio/scripts/run_app.sh
set -euo pipefail

APP_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$APP_ROOT"

export OPENCV_IO_ENABLE_OPENEXR=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

export TRELLIS_LOCAL_HOST="${TRELLIS_LOCAL_HOST:-127.0.0.1}"
export TRELLIS_LOCAL_PORT="${TRELLIS_LOCAL_PORT:-7860}"

if [ "$TRELLIS_LOCAL_HOST" = "0.0.0.0" ]; then
  echo "WARNING: LAN mode is enabled. The app will bind to 0.0.0.0."
fi

if ! python - <<'PY' >/dev/null 2>&1
import fastapi
import uvicorn
PY
then
  echo "Error: FastAPI/Uvicorn app dependencies are missing from the active Python environment."
  echo "Activate the trellis2 Conda environment, then run:"
  echo "  conda activate trellis2"
  echo "  ./scripts/install_app_deps.sh"
  exit 1
fi

if ! python - <<'PY' >/dev/null 2>&1
import torch
raise SystemExit(0 if torch.cuda.is_available() else 1)
PY
then
  echo "WARNING: PyTorch CUDA is not available in the active Python environment."
  echo "The UI can start, but real TRELLIS.2 generation will fail until TRELLIS.2 dependencies are installed."
fi

echo "Starting Trellis Local Studio at http://${TRELLIS_LOCAL_HOST}:${TRELLIS_LOCAL_PORT}"
python -m uvicorn app.main:app \
  --host "$TRELLIS_LOCAL_HOST" \
  --port "$TRELLIS_LOCAL_PORT"

