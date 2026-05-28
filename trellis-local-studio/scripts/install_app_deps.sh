#!/usr/bin/env bash
# Script: install_app_deps.sh
# Location: trellis-local-studio/scripts/install_app_deps.sh
set -euo pipefail

APP_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$APP_ROOT"

echo "Installing Trellis Local Studio app dependencies into the active Python environment..."
python -m pip install -r requirements-app.txt
echo "App dependencies installed."

