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

echo "Starting Trellis Local Studio at http://${TRELLIS_LOCAL_HOST}:${TRELLIS_LOCAL_PORT}"
python3 -m uvicorn app.main:app \
  --host "$TRELLIS_LOCAL_HOST" \
  --port "$TRELLIS_LOCAL_PORT"

