# Changelog

## Unreleased

### Added

- Generation resolution control (512 / 1024 / 1536) wired to official TRELLIS.2 `pipeline_type` values.
- Trellis Local Studio scaffold under `trellis-local-studio/`.
- Added FastAPI backend with local-only defaults and required API endpoints.
- Added static browser UI with dashboard, generation, queue, results, system, settings, logs, and help sections.
- Added quality presets and advanced export option validation.
- Added lazy TRELLIS.2 engine wrapper and CLI generation entry point.
- Added sequential job queue, metadata writing, and job logs.
- Added GPU/system inspection helpers and CUDA cache controls.
- Added setup, run, GPU check, model download, desktop launcher, stop, and open-output scripts.
- Added Miniforge and app-dependency helper scripts for local Ubuntu setup.
- Added `bootstrap_local.sh` to chain local setup and optionally start the app.
- Added `prepare_cuda_glibc_patch.sh` to build CUDA extensions on Ubuntu 26 / glibc 2.41 without sudo.
- Added build, functionality, user, troubleshooting, and architecture documentation.

### Changed

- Quality presets now set generation resolution (512 / 1024 / 1536), not just GLB export settings.
- Root documentation now points users to Trellis Local Studio while preserving the upstream TRELLIS.2 README content below.

### Fixed

- Preserved the Custom preset label when users choose Custom without overriding every field.
- Cleaned partial job folders when request validation raises an HTTP error.
- Exposed metadata downloads for failed jobs that still write metadata.
- Added runtime artifact ignore rules for local inputs, outputs, cache, logs, and config.
- Updated the desktop launcher to open the local browser URL after starting the app.
- Hardened local setup scripts so missing Conda, CUDA Toolkit/nvcc, and app dependencies produce actionable errors.
- Fixed `install_trellis2.sh` to source Conda shell hooks before upstream `setup.sh` calls `conda activate`.
- Fixed local bootstrap/install flow for Ubuntu 26: reuse existing `trellis2` env non-interactively, install flash-attn from the official prebuilt wheel when source builds fail, use `gcc-13` for CUDA extensions, and apply a shadow CUDA header patch for glibc 2.41 `math_functions.h` conflicts.
- Updated `run_app.sh` to auto-activate the `trellis2` Conda environment when available.
- Fixed `No module named 'trellis2'` during generation by adding the upstream TRELLIS.2 repo root to `sys.path` / `PYTHONPATH`.
- Fixed DINOv3 feature extraction with transformers 5.x (`model.layer` moved to `model.model.layer`).
- Fixed GLB export failures caused by `pillow-simd` breaking WebP export; setup now installs standard Pillow only.
- Default GLB export now uses PNG/JPEG textures (`extension_webp=false`) for Blender/DCC compatibility; added `convert_glb_for_blender.py` for existing WebP GLBs.
- Added Hugging Face setup/check script and clearer errors for gated DINOv3 and RMBG-2.0 model access during TRELLIS.2 load.

### Known Issues

- Full TRELLIS.2 generation has not been smoke-tested end-to-end in this session; the local app, GPU diagnostics, and dependency imports were verified on RTX 3090.
- Batch summary CSV/JSON files are not implemented yet.
- Job history is in memory while the app process runs, though output artifacts remain on disk.

