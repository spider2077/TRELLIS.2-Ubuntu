#!/usr/bin/env bash
# Script: install_miniforge.sh
# Location: trellis-local-studio/scripts/install_miniforge.sh
set -euo pipefail

INSTALL_DIR="${MINIFORGE_HOME:-$HOME/miniforge3}"
INSTALLER="/tmp/Miniforge3-Linux-x86_64.sh"
URL="https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh"

if command -v conda >/dev/null 2>&1; then
  echo "conda is already available: $(command -v conda)"
  conda --version
  exit 0
fi

if [ -d "$INSTALL_DIR" ]; then
  echo "Miniforge directory already exists: $INSTALL_DIR"
  echo "Enable it with:"
  echo "  source \"$INSTALL_DIR/etc/profile.d/conda.sh\""
  exit 0
fi

echo "Downloading Miniforge installer..."
curl -L "$URL" -o "$INSTALLER"

echo "Installing Miniforge to $INSTALL_DIR..."
bash "$INSTALLER" -b -p "$INSTALL_DIR"

# shellcheck disable=SC1091
source "$INSTALL_DIR/etc/profile.d/conda.sh"
conda init bash

echo
echo "Miniforge installed."
echo "Open a new terminal, or run:"
echo "  source \"$INSTALL_DIR/etc/profile.d/conda.sh\""

