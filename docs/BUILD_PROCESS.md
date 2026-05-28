# Build Process

This document tracks how to build Trellis Local Studio on Ubuntu Desktop for local TRELLIS.2 image-to-3D generation.

## Commands Used During This Implementation Slice

The repository was updated to the latest `main` before work began:

```bash
git pull origin main
git checkout -b cursor/trellis-local-studio-scaffold-3e3d
```

The app scaffold directories were created under `trellis-local-studio/`, with documentation under `docs/`.

No TRELLIS.2 CUDA dependency installation was run in this cloud environment because GPU validation must happen on the target RTX 3090 workstation. Lightweight app dependencies were installed for API smoke checks with:

```bash
python3 -m pip install --user -r trellis-local-studio/requirements-app.txt
```

A temporary virtualenv attempt failed because `python3.12-venv` is not installed in the cloud image:

```bash
python3 -m venv /tmp/trellis-local-studio-venv
# error: ensurepip is not available; install python3.12-venv
```

The direct `pip --user` install was used only for lightweight FastAPI validation.


## One-Command Local Bootstrap

For local Ubuntu setup, use:

```bash
cd trellis-local-studio
./scripts/bootstrap_local.sh --run
```

The bootstrap script performs the normal setup sequence and stops with CUDA Toolkit 12.4 instructions if `nvcc` is not available.

Use `--skip-system-deps` if apt dependencies are already installed:

```bash
./scripts/bootstrap_local.sh --skip-system-deps --run
```

## System Preparation

```bash
cd trellis-local-studio
./scripts/install_system_deps.sh
```

This installs common build/runtime dependencies:

- git and git-lfs
- wget/curl
- build-essential, cmake, ninja
- ffmpeg
- OpenGL/Glib runtime packages
- libjpeg development headers

## NVIDIA Driver Check

```bash
cd trellis-local-studio
./scripts/check_gpu.sh
```

Expected:

- `nvidia-smi` works.
- An NVIDIA RTX 3090 or other >=24 GB VRAM CUDA GPU is visible.
- PyTorch reports CUDA availability after the Python environment is installed.

## CUDA Toolkit Check

TRELLIS.2 recommends CUDA Toolkit 12.4. On Ubuntu 26, prefer an isolated Conda/Mamba environment and set:

```bash
export CUDA_HOME=/usr/local/cuda-12.4
export PATH="$CUDA_HOME/bin:$PATH"
export LD_LIBRARY_PATH="$CUDA_HOME/lib64:${LD_LIBRARY_PATH:-}"
```

before compiling CUDA extensions.

## Conda/Mamba Setup and TRELLIS.2 Install

If `conda` is not installed, install Miniforge first:

```bash
cd trellis-local-studio
./scripts/install_miniforge.sh
source "$HOME/miniforge3/etc/profile.d/conda.sh"
```

Confirm CUDA Toolkit is installed. `nvidia-smi` showing CUDA 13.0 only means the driver supports that runtime; `nvcc --version` must also work for CUDA extension builds.

For CUDA Toolkit 12.4:

```bash
export CUDA_HOME=/usr/local/cuda-12.4
export PATH="$CUDA_HOME/bin:$PATH"
export LD_LIBRARY_PATH="$CUDA_HOME/lib64:${LD_LIBRARY_PATH:-}"
```

From `trellis-local-studio/`:

```bash
./scripts/install_trellis2.sh
```

This script runs the root TRELLIS.2 setup from the current repository checkout:

```bash
. ./setup.sh --new-env --basic --flash-attn --nvdiffrast --nvdiffrec --cumesh --o-voxel --flexgemm
```

Then it installs app dependencies:

```bash
python3 -m pip install -r trellis-local-studio/requirements-app.txt
```

## Model Download / Preload

After the environment is active:

```bash
cd trellis-local-studio
python3 scripts/download_model.py
```

The app also lazy-loads `microsoft/TRELLIS.2-4B` on first generation or when pressing "Preload model" in the UI.

## First Test Run

```bash
cd trellis-local-studio
./scripts/run_app.sh
```

Open:

```text
http://127.0.0.1:7860
```

CLI smoke path:

```bash
cd trellis-local-studio
python3 -m app.cli.generate --input input/test.png --preset balanced --output output/test
```

## Known Ubuntu 26 Issues

- CUDA Toolkit and system compiler versions may be newer than upstream TRELLIS.2 expects.
- Prefer CUDA Toolkit 12.4 and the Conda environment created by `setup.sh`.
- If CUDA extensions fail to compile, confirm `CUDA_HOME`, `nvcc --version`, driver version, and PyTorch CUDA wheel compatibility.

## Known RTX 3090 Limitations

- 24 GB VRAM is the minimum class for TRELLIS.2.
- Experimental / Max settings may fail with CUDA out-of-memory.
- The app queues one generation at a time by default.

