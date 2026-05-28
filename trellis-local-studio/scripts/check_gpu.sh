#!/usr/bin/env bash
# Script: check_gpu.sh
# Location: trellis-local-studio/scripts/check_gpu.sh
set -euo pipefail

echo "Checking NVIDIA GPU..."
if command -v nvidia-smi >/dev/null 2>&1; then
  nvidia-smi
else
  echo "nvidia-smi not found. Install/check the NVIDIA driver."
fi

echo
echo "Checking CUDA compiler..."
if command -v nvcc >/dev/null 2>&1; then
  nvcc --version
else
  echo "nvcc not found. CUDA Toolkit may not be installed or PATH is not set."
fi

echo
echo "Checking Conda..."
if command -v conda >/dev/null 2>&1; then
  conda --version
  echo "active conda env: ${CONDA_DEFAULT_ENV:-none}"
else
  echo "conda not found. Run ./scripts/install_miniforge.sh before installing TRELLIS.2."
fi

echo
echo "Checking Python..."
python --version || python3 --version
python - <<'PY'
import sys
major, minor = sys.version_info[:2]
if (major, minor) != (3, 10):
    print("WARNING: TRELLIS.2 setup creates/uses Python 3.10 in Conda. Do not use system Python for generation.")
PY

echo
echo "Checking CUDA_HOME..."
echo "CUDA_HOME=${CUDA_HOME:-not set}"
if [ -n "${CUDA_HOME:-}" ] && [ -d "$CUDA_HOME" ]; then
  echo "CUDA_HOME exists."
else
  echo "CUDA_HOME is missing or does not exist. CUDA Toolkit 12.4 is recommended."
fi

echo
echo "Checking PyTorch CUDA..."
python - <<'PY'
try:
    import torch
except Exception as exc:
    print("torch import failed:", exc)
else:
    print("torch:", torch.__version__)
    print("cuda available:", torch.cuda.is_available())
    if torch.cuda.is_available():
        props = torch.cuda.get_device_properties(0)
        print("gpu:", torch.cuda.get_device_name(0))
        print("vram gb:", props.total_memory / 1024**3)
        if props.total_memory < 24 * 1024**3:
            print("WARNING: TRELLIS.2 targets at least 24 GB VRAM.")
PY
