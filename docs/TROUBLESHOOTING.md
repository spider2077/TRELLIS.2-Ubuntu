# Troubleshooting

## `nvidia-smi` Not Working

- Symptom: `scripts/check_gpu.sh` says `nvidia-smi` is not found or fails.
- Likely cause: NVIDIA driver is missing or not loaded.
- Check: `nvidia-smi`.
- Fix: install/reinstall the NVIDIA driver and reboot.


## Local Setup Stops With `conda: command not found`

- Symptom: `./scripts/install_trellis2.sh` prints `conda: command not found`.
- Likely cause: Miniforge, Miniconda, or Anaconda is not installed or not initialized in the terminal.
- Fix:

```bash
cd trellis-local-studio
./scripts/install_miniforge.sh
source "$HOME/miniforge3/etc/profile.d/conda.sh"
./scripts/install_trellis2.sh
```

Open a new terminal after installation if `conda init bash` changed your shell startup files.

## Driver Reports CUDA 13.0 But `nvcc` Is Missing

- Symptom: `nvidia-smi` shows `CUDA Version: 13.0`, but `check_gpu.sh` says `nvcc not found`.
- Likely cause: the NVIDIA driver is installed, but the CUDA Toolkit compiler is not installed.
- Important: the CUDA version shown by `nvidia-smi` is the maximum driver-supported runtime, not proof that the CUDA Toolkit exists.
- Fix: install CUDA Toolkit 12.4, then set:

```bash
export CUDA_HOME=/usr/local/cuda-12.4
export PATH="$CUDA_HOME/bin:$PATH"
export LD_LIBRARY_PATH="$CUDA_HOME/lib64:${LD_LIBRARY_PATH:-}"
```

## App Fails With `No module named uvicorn`

- Symptom: `./scripts/run_app.sh` prints `/usr/bin/python3: No module named uvicorn` or a missing FastAPI/Uvicorn error.
- Likely cause: the app was started with system Python, or app dependencies were not installed because TRELLIS.2 setup stopped earlier.
- Fix:

```bash
cd trellis-local-studio
source "$HOME/miniforge3/etc/profile.d/conda.sh"
conda activate trellis2
./scripts/install_app_deps.sh
./scripts/run_app.sh
```

## Job Fails With `No module named 'trellis2'`

- Symptom: a generation job starts, then fails while loading the model with `No module named 'trellis2'`.
- Likely cause: the app process could not see the upstream TRELLIS.2 Python package in the repository root.
- Fix: pull the latest app code, restart the app, then retry:

```bash
cd trellis-local-studio
./scripts/stop_app.sh
./scripts/run_app.sh
```

The app adds the parent repository root to `PYTHONPATH` automatically. If you start Uvicorn manually, run it from `trellis-local-studio` after activating `conda activate trellis2`.

## System Python Is 3.14

- Symptom: `check_gpu.sh` shows Python 3.14.
- Likely cause: Ubuntu system Python is being used.
- Fix: use the `trellis2` Conda environment created by TRELLIS.2 setup. TRELLIS.2 setup creates Python 3.10, which is the intended runtime for this app.

## CUDA Not Found

- Symptom: CUDA extensions fail to build or `nvcc` is missing.
- Likely cause: CUDA Toolkit is not installed or `PATH` is not set.
- Check: `nvcc --version` and `echo $CUDA_HOME`.
- Fix: install CUDA Toolkit 12.4 and set `CUDA_HOME=/usr/local/cuda-12.4`.

## PyTorch CUDA Not Available

- Symptom: PyTorch imports but reports `cuda available: False`.
- Likely cause: CPU-only PyTorch wheel or driver/toolkit mismatch.
- Check: `python3 -c "import torch; print(torch.__version__, torch.cuda.is_available())"`.
- Fix: reinstall the PyTorch CUDA wheel used by TRELLIS.2 setup.

## CUDA Out of Memory

- Symptom: job fails with CUDA OOM.
- Likely cause: RTX 3090 VRAM pressure or export settings too high.
- Fix:
  - Use Draft or Balanced preset.
  - Lower texture size.
  - Lower decimation target.
  - Close other GPU apps.
  - Restart the app to unload VRAM.

## Model Download Failure

- Symptom: first generation or preload fails while downloading model files.
- Likely cause: internet/cache/Hugging Face issue.
- Check: `python3 scripts/download_model.py`.
- Fix: verify network access and Hugging Face cache permissions.

## Gated Hugging Face Model / `401 Client Error`

- Symptom: job fails while loading the model with `You are trying to access a gated repo`, `401 Client Error`, or `403 Client Error`.
- Likely cause: TRELLIS.2 depends on gated Hugging Face models and access has not been approved yet. Common blockers:
  - `facebook/dinov3-vitl16-pretrain-lvd1689m`
  - `briaai/RMBG-2.0` (background removal)
- Fix:

```bash
# 1. In a browser, sign in and request access on BOTH pages:
#    https://huggingface.co/facebook/dinov3-vitl16-pretrain-lvd1689m
#    https://huggingface.co/briaai/RMBG-2.0

cd trellis-local-studio
source "$HOME/miniforge3/etc/profile.d/conda.sh"
conda activate trellis2
hf auth login
./scripts/setup_huggingface.sh --check --download
./scripts/stop_app.sh
./scripts/run_app.sh
```

- Non-interactive option: create a read token at https://huggingface.co/settings/tokens then run:

```bash
HF_TOKEN=your_read_token hf auth login --token "$HF_TOKEN"
./scripts/setup_huggingface.sh --check --download
```

## Hugging Face Cache Problems

- Symptom: model downloads repeatedly or cannot write cache.
- Likely cause: cache folder permissions or disk space.
- Check: `df -h` and Hugging Face cache directory permissions.
- Fix: free disk space or set `HF_HOME` to a writable folder.

## Invalid Image Upload

- Symptom: upload returns unsupported format or invalid image.
- Likely cause: non-image file or unsupported extension.
- Fix: use `.png`, `.jpg`, `.jpeg`, or `.webp`.

## `'DINOv3ViTModel' object has no attribute 'layer'`

- Symptom: generation fails during TRELLIS.2 inference after models load.
- Likely cause: newer `transformers` (5.x) changed the DINOv3 module layout.
- Fix: pull the latest app/TRELLIS.2 code, restart the app, and retry. The feature extractor now supports both `.layer` and `.model.layer`.

## GLB Export Fails With `PIL._webp` / `HAVE_WEBPANIM`

- Symptom: generation completes, then export fails with `module 'PIL._webp' has no attribute 'HAVE_WEBPANIM'`.
- Likely cause: `pillow-simd` was installed and overrides standard Pillow, breaking WebP GLB export.
- Fix:

```bash
source "$HOME/miniforge3/etc/profile.d/conda.sh"
conda activate trellis2
pip uninstall -y Pillow-SIMD
pip install --force-reinstall pillow
cd trellis-local-studio
./scripts/stop_app.sh
./scripts/run_app.sh
```

Then retry the job.

## GLB Export Failure

- Symptom: generation runs but GLB export fails.
- Likely cause: O-Voxel dependency issue, CUDA error, or memory pressure.
- Check: the job log.
- Fix: confirm `o-voxel` installed, lower export settings, and rerun.

## Preview Render Failure

- Symptom: GLB exists but preview video is missing.
- Likely cause: render dependency or memory issue.
- Fix: use the GLB output; preview failures are logged and do not block GLB export.

## Ubuntu 26 Dependency Issue

- Symptom: packages or CUDA extensions fail during install.
- Likely cause: newer system compiler/libraries than upstream tested.
- Fix: use Conda isolation, CUDA Toolkit 12.4, and the exact TRELLIS.2 setup flags in `docs/BUILD_PROCESS.md`.

Common Ubuntu 26 fixes used by Trellis Local Studio:

```bash
cd trellis-local-studio
./scripts/bootstrap_local.sh --skip-system-deps --run
```

Notes:

- Use `--skip-system-deps` if `sudo apt` is unavailable in the current terminal. Ensure `git`, `ffmpeg`, `build-essential`, `libjpeg-dev`, `zlib1g-dev`, `gcc-13`, and `g++-13` are already installed.
- If bootstrap stops at `Remove existing environment?`, pull the latest scripts. The installer now reuses an existing `trellis2` environment instead of prompting.
- If CUDA extension builds fail with `exception specification is incompatible` for `cospi` / `sinpi` / `rsqrt`, run the installer again. It applies a shadow CUDA header patch under `~/.local/share/trellis-local-studio/shadow-cuda`.
- If `flash-attn` fails to build, the installer falls back to the official prebuilt wheel for PyTorch 2.6 + CUDA 12.4 + Python 3.10.


## `CondaError: Run 'conda init' before 'conda activate'`

- Symptom: `install_trellis2.sh` creates the `trellis2` environment, then upstream `setup.sh` fails at `conda activate trellis2`.
- Likely cause: Conda's shell hook was not sourced inside the installer process.
- Fix after pulling the latest script:

```bash
cd trellis-local-studio
source "$HOME/miniforge3/etc/profile.d/conda.sh"
./scripts/install_trellis2.sh
```

If you cannot pull the latest script yet, run the upstream setup from the repository root in the same shell where `conda.sh` is sourced:

```bash
source "$HOME/miniforge3/etc/profile.d/conda.sh"
cd ..
export CUDA_HOME=/usr/local/cuda-12.4
export PATH="$CUDA_HOME/bin:$PATH"
export LD_LIBRARY_PATH="$CUDA_HOME/lib64:${LD_LIBRARY_PATH:-}"
. ./setup.sh --new-env --basic --flash-attn --nvdiffrast --nvdiffrec --cumesh --o-voxel --flexgemm
conda activate trellis2
python -m pip install -r trellis-local-studio/requirements-app.txt
```

## Conda Environment Issue

- Symptom: `conda activate trellis2` fails or packages import from the wrong environment.
- Likely cause: Conda not initialized or wrong shell.
- Fix: initialize Conda for your shell and reactivate `trellis2`.

## App Starts But Page Does Not Open

- Symptom: terminal says app started, browser cannot connect.
- Likely cause: wrong URL or port.
- Check: open `http://127.0.0.1:7860`.
- Fix: verify the port printed by `scripts/run_app.sh`.

## Port Already In Use

- Symptom: Uvicorn reports address already in use.
- Likely cause: another app is using port 7860.
- Fix:

```bash
cd trellis-local-studio
TRELLIS_LOCAL_PORT=7861 ./scripts/run_app.sh
```

