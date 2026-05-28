# Architecture

```text
Browser UI
   ↓
FastAPI backend
   ↓
Job queue
   ↓
TRELLIS.2 engine wrapper
   ↓
TRELLIS.2 model on RTX 3090
   ↓
GLB / preview / metadata / logs
```

## Folder Structure

```text
trellis-local-studio/
├── README.md
├── requirements-app.txt
├── scripts/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── cli/
│   ├── engine/
│   ├── jobs/
│   ├── utils/
│   └── web/
├── input/
├── output/
├── cache/
└── logs/
```

Root `docs/` contains the build, user, functionality, troubleshooting, architecture, and changelog documentation.

## Backend API Overview

Implemented endpoints:

- `GET /`
- `GET /api/health`
- `GET /api/system`
- `GET /api/options`
- `POST /api/jobs`
- `GET /api/jobs`
- `GET /api/jobs/{job_id}`
- `GET /api/jobs/{job_id}/download/glb`
- `GET /api/jobs/{job_id}/download/preview`
- `GET /api/jobs/{job_id}/download/metadata`
- `GET /api/jobs/{job_id}/log`
- `GET /api/model/status`
- `POST /api/model/preload`
- `POST /api/model/unload`
- `POST /api/cache/clear`

## Frontend Overview

The frontend is a static local browser UI in `app/web/`. It includes:

- Dashboard / Home
- New Generation
- Job Queue
- Results / History
- System / GPU Info
- Settings
- Logs / Troubleshooting
- Help / Usage

It does not make remote analytics calls.

## Job Queue Design

`app/jobs/job_store.py` keeps an in-memory job list for the running app process. `app/jobs/worker.py` uses an `asyncio.Queue` and runs jobs sequentially by default.

Each job writes durable artifacts to its output folder so generated files remain after app restart.

## TRELLIS.2 Engine Wrapper Design

`app/engine/trellis_engine.py` lazy-loads `Trellis2ImageTo3DPipeline` from the official TRELLIS.2 code. The UI and API call the wrapper, not TRELLIS.2 internals directly.

The wrapper:

- loads the model on demand
- runs `pipeline.run(image)[0]`
- applies the nvdiffrast simplify limit
- exports GLB through `o_voxel.postprocess.to_glb`
- optionally renders a preview video
- clears CUDA cache after generation attempts

## GPU Guard Design

`app/engine/gpu_guard.py` serializes generation jobs unless `TRELLIS_UNSAFE_PARALLEL_JOBS=1` is set. This protects the RTX 3090 target from default parallel jobs.

## Output Folder Lifecycle

The app creates a timestamped job folder under `trellis-local-studio/output/`. It stores original input, normalized input, logs, metadata, and outputs.

## Configuration and Environment Variables

- `TRELLIS_LOCAL_HOST`: default `127.0.0.1`
- `TRELLIS_LOCAL_PORT`: default `7860`
- `TRELLIS_MODEL_NAME`: default `microsoft/TRELLIS.2-4B`
- `TRELLIS_OUTPUT_DIR`: optional output folder override
- `TRELLIS_UNSAFE_PARALLEL_JOBS=1`: disables sequential GPU guard
- `CUDA_HOME`: recommended `/usr/local/cuda-12.4`

## Security / Local-Only Design

The app binds to `127.0.0.1` by default. LAN mode requires explicit configuration with `TRELLIS_LOCAL_HOST=0.0.0.0` and prints a warning.

No accounts, telemetry, cloud sync, or remote image upload behavior is implemented.

