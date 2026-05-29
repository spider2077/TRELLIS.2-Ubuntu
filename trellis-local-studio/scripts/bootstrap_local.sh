#!/usr/bin/env bash
# Script: bootstrap_local.sh
# Location: trellis-local-studio/scripts/bootstrap_local.sh
set -euo pipefail

APP_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$APP_ROOT"

RUN_APP=false
SKIP_SYSTEM_DEPS=false

usage() {
  cat <<'EOF'
Usage: ./scripts/bootstrap_local.sh [OPTIONS]

Options:
  --run                Start the local web app after setup completes.
  --skip-system-deps   Skip apt-based system dependency installation.
  -h, --help           Show this help.

This script helps bootstrap Trellis Local Studio on a local Ubuntu workstation.
It installs/loads Miniforge, checks CUDA Toolkit/nvcc, installs TRELLIS.2
dependencies, installs app dependencies, runs diagnostics, and optionally starts
the app.
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --run)
      RUN_APP=true
      shift
      ;;
    --skip-system-deps)
      SKIP_SYSTEM_DEPS=true
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      usage
      exit 1
      ;;
  esac
done

echo "== Trellis Local Studio local bootstrap =="
echo "App root: $APP_ROOT"

if [ "$SKIP_SYSTEM_DEPS" = false ]; then
  echo
  echo "== Installing system dependencies =="
  if ! ./scripts/install_system_deps.sh; then
    echo
    echo "Warning: system dependency install failed (sudo may be unavailable)."
    echo "If git, ffmpeg, build tools, and libjpeg-dev are already installed,"
    echo "rerun with: ./scripts/bootstrap_local.sh --skip-system-deps --run"
    exit 1
  fi
fi

echo
echo "== Loading or installing Conda/Miniforge =="
if ! command -v conda >/dev/null 2>&1; then
  if [ ! -f "$HOME/miniforge3/etc/profile.d/conda.sh" ]; then
    ./scripts/install_miniforge.sh
  fi
  # shellcheck disable=SC1091
  source "$HOME/miniforge3/etc/profile.d/conda.sh"
else
  # Load the shell hook when conda exists but the shell function is not active.
  for candidate in \
    "$HOME/miniforge3/etc/profile.d/conda.sh" \
    "$HOME/miniconda3/etc/profile.d/conda.sh" \
    "$HOME/anaconda3/etc/profile.d/conda.sh"; do
    if [ -f "$candidate" ]; then
      # shellcheck disable=SC1090
      source "$candidate"
      break
    fi
  done
fi

if ! command -v conda >/dev/null 2>&1; then
  echo "Error: conda is still unavailable after Miniforge setup."
  echo "Open a new terminal, then rerun this script."
  exit 1
fi

conda --version

echo
echo "== Checking CUDA Toolkit =="
export SYSTEM_CUDA_HOME="${CUDA_HOME:-/usr/local/cuda-12.4}"
export CUDA_HOME="$SYSTEM_CUDA_HOME"
export PATH="$CUDA_HOME/bin:$PATH"
export LD_LIBRARY_PATH="$CUDA_HOME/lib64:${LD_LIBRARY_PATH:-}"

if [ ! -d "$CUDA_HOME" ] || ! command -v nvcc >/dev/null 2>&1; then
  echo "CUDA Toolkit/nvcc is not available at CUDA_HOME=$CUDA_HOME."
  echo
  echo "Install CUDA Toolkit 12.4 first. Example:"
  echo "  cd /tmp"
  echo "  wget https://developer.download.nvidia.com/compute/cuda/12.4.1/local_installers/cuda_12.4.1_550.54.15_linux.run"
  echo "  sudo sh cuda_12.4.1_550.54.15_linux.run --silent --toolkit --override"
  echo
  echo "Then rerun:"
  echo "  export CUDA_HOME=/usr/local/cuda-12.4"
  echo "  export PATH=\"\$CUDA_HOME/bin:\$PATH\""
  echo "  export LD_LIBRARY_PATH=\"\$CUDA_HOME/lib64:\${LD_LIBRARY_PATH:-}\""
  echo "  ./scripts/bootstrap_local.sh --run"
  exit 1
fi

nvcc --version

echo
echo "== Installing TRELLIS.2 dependencies =="
./scripts/install_trellis2.sh

echo
echo "== Installing app dependencies =="
conda activate trellis2
./scripts/install_app_deps.sh

echo
echo "== Running diagnostics =="
./scripts/check_gpu.sh

echo
echo "Bootstrap complete."
echo "To start later, run:"
echo "  cd \"$APP_ROOT\""
echo "  source \"$HOME/miniforge3/etc/profile.d/conda.sh\""
echo "  conda activate trellis2"
echo "  ./scripts/run_app.sh"

if [ "$RUN_APP" = true ]; then
  echo
  echo "== Starting Trellis Local Studio =="
  ./scripts/run_app.sh
fi

