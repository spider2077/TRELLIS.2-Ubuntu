#!/usr/bin/env bash
# Script: install_trellis2.sh
# Location: trellis-local-studio/scripts/install_trellis2.sh
set -euo pipefail

APP_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$(cd "$APP_ROOT/.." && pwd)"
cd "$REPO_ROOT"

export CUDA_HOME="${CUDA_HOME:-/usr/local/cuda-12.4}"
export SYSTEM_CUDA_HOME="$CUDA_HOME"
export PATH="$CUDA_HOME/bin:$PATH"
export LD_LIBRARY_PATH="$CUDA_HOME/lib64:${LD_LIBRARY_PATH:-}"
export CC="${CC:-gcc-13}"
export CXX="${CXX:-g++-13}"
export CUDAHOSTCXX="${CUDAHOSTCXX:-g++-13}"
export NVCC_PREPEND_FLAGS="${NVCC_PREPEND_FLAGS:--allow-unsupported-compiler}"

CONDA_SH=""
for candidate in \
  "$HOME/miniforge3/etc/profile.d/conda.sh" \
  "$HOME/miniconda3/etc/profile.d/conda.sh" \
  "$HOME/anaconda3/etc/profile.d/conda.sh"; do
  if [ -f "$candidate" ]; then
    CONDA_SH="$candidate"
    break
  fi
done

if [ -n "$CONDA_SH" ]; then
  # shellcheck disable=SC1090
  . "$CONDA_SH"
fi

if ! command -v conda >/dev/null 2>&1; then
  echo "Error: conda was not found."
  echo "Install Miniforge first, then open a new terminal or source conda.sh:"
  echo "  ./scripts/install_miniforge.sh"
  echo '  source "$HOME/miniforge3/etc/profile.d/conda.sh"'
  exit 1
fi

if [ ! -d "$CUDA_HOME" ]; then
  echo "Error: CUDA_HOME does not exist: $CUDA_HOME"
  echo "Install CUDA Toolkit 12.4 or set CUDA_HOME to the toolkit path before running this script."
  echo "Your NVIDIA driver can report CUDA 13.0 while the CUDA Toolkit/nvcc is still missing."
  exit 1
fi

if ! command -v nvcc >/dev/null 2>&1; then
  echo "Error: nvcc was not found in PATH."
  echo 'Install CUDA Toolkit 12.4 or set PATH so "$CUDA_HOME/bin/nvcc" is available.'
  exit 1
fi

# shellcheck disable=SC1091
source "$APP_ROOT/scripts/prepare_cuda_glibc_patch.sh"

echo "Installing TRELLIS.2 dependencies from current repository checkout."
echo "CUDA_HOME=$CUDA_HOME"

SETUP_ARGS=(--basic --flash-attn --nvdiffrast --nvdiffrec --cumesh --o-voxel --flexgemm)
if conda env list | awk '{print $1}' | grep -qx trellis2; then
  echo "Reusing existing trellis2 conda environment."
  conda activate trellis2
  conda install -y zlib >/dev/null 2>&1 || true
  if ! python -c "import torch" >/dev/null 2>&1; then
    echo "Installing PyTorch into existing trellis2 environment..."
    pip install torch==2.6.0 torchvision==0.21.0 --index-url https://download.pytorch.org/whl/cu124
  fi
else
  SETUP_ARGS=(--new-env "${SETUP_ARGS[@]}")
fi

. ./setup.sh "${SETUP_ARGS[@]}"

echo "Installing Trellis Local Studio app dependencies."
python -m pip install -r "$APP_ROOT/requirements-app.txt"

echo "TRELLIS.2 environment should now be installed."
echo "Activate with: conda activate trellis2"

