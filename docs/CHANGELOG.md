# Changelog

## Unreleased

### Added

- Added Trellis Local Studio scaffold under `trellis-local-studio/`.
- Added FastAPI backend with local-only defaults and required API endpoints.
- Added static browser UI with dashboard, generation, queue, results, system, settings, logs, and help sections.
- Added quality presets and advanced export option validation.
- Added lazy TRELLIS.2 engine wrapper and CLI generation entry point.
- Added sequential job queue, metadata writing, and job logs.
- Added GPU/system inspection helpers and CUDA cache controls.
- Added setup, run, GPU check, model download, desktop launcher, stop, and open-output scripts.
- Added Miniforge and app-dependency helper scripts for local Ubuntu setup.
- Added build, functionality, user, troubleshooting, and architecture documentation.

### Changed

- Root documentation now points users to Trellis Local Studio while preserving the upstream TRELLIS.2 README content below.

### Fixed

- Preserved the Custom preset label when users choose Custom without overriding every field.
- Cleaned partial job folders when request validation raises an HTTP error.
- Exposed metadata downloads for failed jobs that still write metadata.
- Added runtime artifact ignore rules for local inputs, outputs, cache, logs, and config.
- Updated the desktop launcher to open the local browser URL after starting the app.
- Hardened local setup scripts so missing Conda, CUDA Toolkit/nvcc, and app dependencies produce actionable errors.
- Fixed `install_trellis2.sh` to source Conda shell hooks before upstream `setup.sh` calls `conda activate`.

### Known Issues

- Full TRELLIS.2 generation has not been smoke-tested in this cloud environment because CUDA/GPU dependencies are target-machine specific.
- Batch summary CSV/JSON files are not implemented yet.
- Job history is in memory while the app process runs, though output artifacts remain on disk.

