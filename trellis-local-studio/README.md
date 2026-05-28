# Trellis Local Studio

Trellis Local Studio is a local Ubuntu Desktop web app for running Microsoft TRELLIS.2 image-to-3D generation on an NVIDIA GPU workstation.

This app uses existing user-provided images as input. It does not create images from text prompts, does not include integrated text-to-image generation, and does not depend on ComfyUI or other image-generation workflows.

## Current Status

This first implementation slice provides:

- FastAPI backend with local-only defaults.
- Browser UI at `http://127.0.0.1:7860`.
- Single image, front/back organizational mode, and multi-file batch queuing.
- Draft, Balanced, High Quality, Experimental / Max, and Custom presets.
- Advanced GLB export options.
- One-job-at-a-time queue for RTX 3090-style memory safety.
- Lazy TRELLIS.2 pipeline loading.
- Metadata and job log files in each output folder.
- GPU/system info endpoints and UI panels.
- CLI wrapper: `python3 -m app.cli.generate --input input/test.png --preset balanced --output output/test`.

The app scaffold is ready for environment-level testing on a CUDA workstation. Full generation requires the TRELLIS.2 dependencies and model weights.

## Hardware and OS

- Ubuntu Desktop, with Ubuntu 26 expected to need careful CUDA/toolchain isolation.
- NVIDIA GPU with at least 24 GB VRAM; RTX 3090 is the target.
- CUDA Toolkit 12.4 is the preferred target unless the installed NVIDIA driver requires a different setup.
- Conda or Mamba environment isolation is recommended.

## Install Summary

From the repository root:

```bash
cd trellis-local-studio
./scripts/check_gpu.sh
./scripts/install_system_deps.sh
```

If `conda` is missing, install Miniforge:

```bash
./scripts/install_miniforge.sh
source "$HOME/miniforge3/etc/profile.d/conda.sh"
```

Install CUDA Toolkit 12.4 if `nvcc` is missing, then set:

```bash
export CUDA_HOME=/usr/local/cuda-12.4
export PATH="$CUDA_HOME/bin:$PATH"
export LD_LIBRARY_PATH="$CUDA_HOME/lib64:${LD_LIBRARY_PATH:-}"
```

Then install TRELLIS.2 and the app dependencies:

```bash
./scripts/install_trellis2.sh
```

If Ubuntu 26 has CUDA/toolchain issues, install CUDA Toolkit 12.4 exactly and ensure:

```bash
export CUDA_HOME=/usr/local/cuda-12.4
```

before running the TRELLIS.2 setup.

## Run

```bash
cd trellis-local-studio
./scripts/check_gpu.sh
./scripts/run_app.sh
```

Open:

```text
http://127.0.0.1:7860
```

The default bind address is `127.0.0.1`. To enable LAN mode, set `TRELLIS_LOCAL_HOST=0.0.0.0`; the app and script will warn when this is enabled.

## Output Folders

Each generation creates a folder under:

```text
trellis-local-studio/output/
```

with files such as:

```text
input_original.ext
input_normalized.png
output.glb
preview.mp4
metadata.json
job.log
```

## Presets

- Draft / Fast: quick tests and smaller outputs.
- Balanced: recommended RTX 3090 default.
- High Quality: heavier settings for better visual output.
- Experimental / Max: high memory risk; may fail on RTX 3090.
- Custom: manual advanced export settings.

## Documentation

See the root `docs/` folder:

- `docs/BUILD_PROCESS.md`
- `docs/FUNCTIONALITY.md`
- `docs/USER_GUIDE.md`
- `docs/TROUBLESHOOTING.md`
- `docs/ARCHITECTURE.md`
- `docs/CHANGELOG.md`

Agent instructions are maintained in root-level `AGENTS.md` and `CLAUDE.md`.

