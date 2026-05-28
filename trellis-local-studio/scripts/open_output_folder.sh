#!/usr/bin/env bash
# Script: open_output_folder.sh
# Location: trellis-local-studio/scripts/open_output_folder.sh
set -euo pipefail

APP_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUTPUT_DIR="${TRELLIS_OUTPUT_DIR:-$APP_ROOT/output}"

mkdir -p "$OUTPUT_DIR"
if command -v xdg-open >/dev/null 2>&1; then
  xdg-open "$OUTPUT_DIR"
else
  echo "Output folder: $OUTPUT_DIR"
fi

