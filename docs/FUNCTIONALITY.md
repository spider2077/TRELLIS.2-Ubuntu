# Functionality

Trellis Local Studio is image-to-3D only. It uses existing user-provided images and does not generate images from text prompts.

## Single-Image Generation

- What it does: queues one image for TRELLIS.2 generation and GLB export.
- What it does not do: it does not create, edit, or synthesize the input image.
- Controls: primary image upload, preset, advanced export options, output basename.
- Backend files: `app/main.py`, `app/jobs/worker.py`, `app/engine/trellis_engine.py`.
- Limitation: full generation requires a CUDA TRELLIS.2 environment and model weights.

## Front/Back Pair Mode

- What it does: stores front and optional back images, lets the user choose the primary image, and generates from that selected image.
- What it does not do: TRELLIS.2 generation is single-image based; both images are not natively fused into one reconstruction.
- Controls: front upload, back upload, primary image selector.
- Backend files: `app/main.py`, `app/utils/image_prep.py`.
- Limitation: secondary image is saved for reference unless a verified multi-view/refinement module is added later.

## Batch Mode

- What it does: the UI accepts multiple primary images and submits one queued job per file.
- What it does not do: failed jobs do not currently create a batch summary CSV/JSON.
- Controls: choose Batch Folder / Multiple Images, select multiple files, choose preset.
- Backend files: `app/web/app.js`, `app/main.py`, `app/jobs/worker.py`.
- Limitation: batch summary files are future work.

## Quality Presets

- Draft / Fast: 250k decimation target, 2048 texture, preview off.
- Balanced: 1M decimation target, 4096 texture, preview on.
- High Quality: 2M decimation target, 4096 texture, preview on.
- Experimental / Max: 4M decimation target, 8192 texture, preview on.
- Custom: manual advanced settings.

Backend file: `app/engine/export_options.py`.

## Advanced Export Options

Implemented controls:

- decimation_target
- texture_size
- remesh
- remesh_band
- remesh_project
- extension_webp
- render_preview
- preview_fps
- preview_turntable_seconds
- output_basename

Validation is implemented in `app/engine/export_options.py`.

## Job Queue Behavior

- Jobs are stored in memory while the app is running.
- Output artifacts are stored on disk under `trellis-local-studio/output/`.
- The worker processes one job at a time by default.
- Statuses currently include `queued`, `loading_model`, `running`, `completed`, and `failed`.

Backend files: `app/jobs/job_store.py`, `app/jobs/worker.py`, `app/engine/gpu_guard.py`.

## GPU / Memory Handling

- `nvidia-smi` information is shown through `/api/system`.
- The app warns when VRAM is below 24 GB.
- CUDA cache is cleared after generation attempts.
- Unsafe parallel jobs require `TRELLIS_UNSAFE_PARALLEL_JOBS=1`.

## Model Preload / Unload

- `/api/model/preload` loads `microsoft/TRELLIS.2-4B`.
- `/api/model/unload` drops the pipeline reference and clears CUDA cache.
- The UI exposes both buttons on the System / GPU page.

## Output Folder Structure

Each job folder contains:

```text
input_original.ext or input_front_original.ext
input_back_original.ext when provided
input_normalized.png
output.glb after success
preview.mp4 when preview succeeds
metadata.json
job.log
```

## Preview Rendering

Preview video rendering is attempted when enabled. GLB export remains the priority; preview failures are logged and do not fail the whole job.

