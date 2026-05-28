#!/usr/bin/env bash
# Script: stop_app.sh
# Location: trellis-local-studio/scripts/stop_app.sh
set -euo pipefail

PORT="${TRELLIS_LOCAL_PORT:-7860}"

if command -v fuser >/dev/null 2>&1; then
  fuser -k "${PORT}/tcp" || true
  echo "Stopped processes listening on port $PORT, if any."
else
  echo "fuser is not installed. Stop the terminal running run_app.sh with Ctrl+C."
fi

