# Troubleshooting

## `nvidia-smi` Not Working

- Symptom: `scripts/check_gpu.sh` says `nvidia-smi` is not found or fails.
- Likely cause: NVIDIA driver is missing or not loaded.
- Check: `nvidia-smi`.
- Fix: install/reinstall the NVIDIA driver and reboot.

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

## Hugging Face Cache Problems

- Symptom: model downloads repeatedly or cannot write cache.
- Likely cause: cache folder permissions or disk space.
- Check: `df -h` and Hugging Face cache directory permissions.
- Fix: free disk space or set `HF_HOME` to a writable folder.

## Invalid Image Upload

- Symptom: upload returns unsupported format or invalid image.
- Likely cause: non-image file or unsupported extension.
- Fix: use `.png`, `.jpg`, `.jpeg`, or `.webp`.

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

