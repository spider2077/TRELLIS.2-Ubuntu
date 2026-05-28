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
echo "Checking Python..."
python3 --version

echo
echo "Checking PyTorch CUDA..."
python3 - <<'PY'
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

