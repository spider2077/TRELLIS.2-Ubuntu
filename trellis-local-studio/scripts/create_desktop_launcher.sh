#!/usr/bin/env bash
# Script: create_desktop_launcher.sh
# Location: trellis-local-studio/scripts/create_desktop_launcher.sh
set -euo pipefail

APP_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DESKTOP_DIR="$HOME/.local/share/applications"
DESKTOP_FILE="$DESKTOP_DIR/trellis-local-studio.desktop"

mkdir -p "$DESKTOP_DIR"

cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Type=Application
Name=Trellis Local Studio
Comment=Local TRELLIS.2 image-to-3D generation
Exec=bash -lc 'cd "$APP_ROOT" && ./scripts/run_app.sh'
Terminal=true
Categories=Graphics;3DGraphics;
EOF

chmod +x "$DESKTOP_FILE"
echo "Created launcher: $DESKTOP_FILE"
echo "Open http://127.0.0.1:7860 after the launcher starts."

