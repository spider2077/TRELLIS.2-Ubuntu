#!/usr/bin/env bash
# Script: install_trellis2.sh
# Location: trellis-local-studio/scripts/install_trellis2.sh
set -euo pipefail

APP_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$(cd "$APP_ROOT/.." && pwd)"
cd "$REPO_ROOT"

export CUDA_HOME="${CUDA_HOME:-/usr/local/cuda-12.4}"
export PATH="$CUDA_HOME/bin:$PATH"
export LD_LIBRARY_PATH="$CUDA_HOME/lib64:${LD_LIBRARY_PATH:-}"

echo "Installing TRELLIS.2 dependencies from current repository checkout."
echo "CUDA_HOME=$CUDA_HOME"
. ./setup.sh --new-env --basic --flash-attn --nvdiffrast --nvdiffrec --cumesh --o-voxel --flexgemm

echo "Installing Trellis Local Studio app dependencies."
python3 -m pip install -r "$APP_ROOT/requirements-app.txt"

echo "TRELLIS.2 environment should now be installed."
echo "Activate with: conda activate trellis2"

