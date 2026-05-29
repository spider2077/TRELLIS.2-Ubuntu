#!/usr/bin/env bash
# Script: install_system_deps.sh
# Location: trellis-local-studio/scripts/install_system_deps.sh
set -euo pipefail

sudo apt update
sudo apt install -y \
  git git-lfs wget curl build-essential cmake ninja-build \
  ffmpeg libgl1 libglib2.0-0 libjpeg-dev zlib1g-dev gcc-13 g++-13

git lfs install

echo "System dependencies installed."

