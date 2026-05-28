# AGENTS.md — Local TRELLIS.2 App Build Spec

## Project Goal

Build a standalone local Ubuntu Desktop app for running **Microsoft TRELLIS.2 image-to-3D generation** on a local NVIDIA RTX 3090 machine.

The app must be **image-to-3D only**.

Do **not** integrate text-to-image, prompt-to-image, Stable Diffusion, ComfyUI, Flux, SDXL, DALL-E, Midjourney-style workflows, or any other image creation model.

The user will provide existing input images. The app should generate 3D assets from those images using TRELLIS.2.

Target machine:

- OS: Ubuntu 26 Desktop
- GPU: NVIDIA RTX 3090, 24 GB VRAM
- Usage: Local-only desktop workstation
- Primary output: GLB with PBR materials
- Secondary output: preview video/image renders if available
- Intended use: Blender, Unity, game props, visual 3D assets, possible later mesh cleanup workflows

---

## Important Constraints

1. **No integrated image generation**
   - No text-to-image model
   - No prompt-based image creation
   - No hidden image-generation dependency
   - No external image generation API
   - The app may accept a text label/name for job organization only, but not for generation.

2. **Local only by default**
   - Default bind address must be `127.0.0.1`
   - Do not expose the app to LAN or internet unless explicitly configured.
   - Do not add account login, telemetry, cloud sync, or remote upload.

3. **TRELLIS.2 official code first**
   - Use the official Microsoft `microsoft/TRELLIS.2` repository as the core engine.
   - Use `microsoft/TRELLIS.2-4B` as the default model.
   - Avoid community forks unless needed for a clearly documented workaround.

4. **Ubuntu 26 warning**
   - TRELLIS.2 is officially tested on Linux, but Ubuntu 26 may have newer system libraries than expected.
   - Prefer Conda/Mamba environment isolation.
   - CUDA Toolkit 12.4 is the preferred target unless the user’s driver/toolkit combination requires adjustment.

5. **RTX 3090 limits**
   - 24 GB VRAM is the minimum class for TRELLIS.2.
   - High-quality settings may still hit VRAM limits.
   - The app must include safe presets and memory-related warnings.

---

## Official TRELLIS.2 Facts To Respect

TRELLIS.2 is a 4B-parameter image-to-3D model that outputs 3D assets with PBR materials.

Official model:

```text
microsoft/TRELLIS.2-4B
```

Official repository:

```text
https://github.com/microsoft/TRELLIS.2
```

Official expected input/output:

```text
Input: single image
Output: 3D mesh / GLB with PBR material attributes
```

Official examples use:

```python
from trellis2.pipelines import Trellis2ImageTo3DPipeline
pipeline = Trellis2ImageTo3DPipeline.from_pretrained("microsoft/TRELLIS.2-4B")
pipeline.cuda()
mesh = pipeline.run(image)[0]
```

Official GLB export uses `o_voxel.postprocess.to_glb(...)` with options such as:

```python
decimation_target = 1000000
texture_size = 4096
remesh = True
remesh_band = 1
remesh_project = 0
extension_webp = True
```

The app must treat exact Python function signatures as version-dependent. Inspect the installed repo before hardcoding unsupported arguments.

---

## App Name

Working name:

```text
Trellis Local Studio
```

Folder name:

```text
trellis-local-studio
```

---

## Recommended Architecture

Use a proper local visual app:

```text
FastAPI backend
+ polished local HTML/JS frontend
+ optional Gradio fallback
+ TRELLIS.2 engine wrapper
+ local job queue
+ local output folder
```

Preferred structure:

```text
trellis-local-studio/
├── AGENTS.md
├── README.md
├── requirements-app.txt
├── scripts/
│   ├── install_system_deps.sh
│   ├── install_trellis2.sh
│   ├── run_app.sh
│   ├── check_gpu.sh
│   └── download_model.py
├── app/
│   ├── main.py
│   ├── config.py
│   ├── engine/
│   │   ├── trellis_engine.py
│   │   ├── export_options.py
│   │   └── gpu_guard.py
│   ├── jobs/
│   │   ├── job_store.py
│   │   └── worker.py
│   ├── utils/
│   │   ├── image_prep.py
│   │   ├── filenames.py
│   │   └── system_info.py
│   └── web/
│       ├── index.html
│       ├── app.js
│       └── style.css
├── input/
├── output/
├── cache/
└── logs/
```

---

## Core User Workflow

The UI should support:

1. Upload/select an image
2. Choose a quality preset
3. Choose export options
4. Click generate
5. Show job status
6. Preview generated result if possible
7. Download/open output folder containing:
   - `.glb`
   - optional `.mp4` preview
   - metadata `.json`
   - copy of input image
   - log file

---

## Required Features

### 1. Image Input

Supported input formats:

```text
.png
.jpg
.jpeg
.webp
```

Recommended image behavior:

- Convert input to RGB/RGBA as needed.
- Preserve alpha channel where possible.
- Allow transparent PNG input.
- Do not auto-generate missing views.
- Do not modify the original file.
- Save a normalized copy in the job folder.

Input options:

```text
single image
front image + back image stored as a paired job, but only front is used for TRELLIS.2 generation unless a future multi-view module is implemented
batch folder mode
```

Important:

TRELLIS.2 official inference is single-image based. If the UI accepts front/back images, label it clearly:

```text
Front/back mode is organizational and experimental. TRELLIS.2 will generate from the selected primary image unless a custom multi-view/refinement module is added later.
```

Do not pretend native multi-view reconstruction exists unless implemented and verified.

---

### 2. Quality Presets

Create user-facing presets that map to export settings and memory expectations.

#### Draft / Fast

Purpose:

```text
quick test, lower output size
```

Suggested defaults:

```python
decimation_target = 250000
texture_size = 2048
remesh = True
remesh_band = 1
remesh_project = 0
extension_webp = True
render_preview = False
```

#### Balanced

Purpose:

```text
normal use on RTX 3090
```

Suggested defaults:

```python
decimation_target = 1000000
texture_size = 4096
remesh = True
remesh_band = 1
remesh_project = 0
extension_webp = True
render_preview = True
```

#### High Quality

Purpose:

```text
best visual asset when VRAM allows
```

Suggested defaults:

```python
decimation_target = 2000000
texture_size = 4096
remesh = True
remesh_band = 1
remesh_project = 0
extension_webp = True
render_preview = True
```

#### Experimental / Max

Purpose:

```text
try maximum quality, may fail on RTX 3090
```

Suggested defaults:

```python
decimation_target = 4000000
texture_size = 8192
remesh = True
remesh_band = 1
remesh_project = 0
extension_webp = True
render_preview = True
```

The app must allow changing these values manually in an Advanced panel.

---

### 3. Advanced Export Options

Expose these options:

```text
decimation_target
texture_size
remesh
remesh_band
remesh_project
extension_webp
render_preview
preview_fps
preview_turntable_seconds
output_basename
```

Suggested validation:

```text
decimation_target: 50,000 to 8,000,000
texture_size: 1024, 2048, 4096, 8192
remesh: true/false
remesh_band: integer, default 1
remesh_project: integer/float, default 0
extension_webp: true/false
render_preview: true/false
preview_fps: 10 to 30
preview_turntable_seconds: 3 to 20
```

Warn that very high `decimation_target` and `texture_size` can increase export time, output size, and memory use.

---

### 4. GPU / Memory Handling

At app startup:

- Run `nvidia-smi`
- Confirm CUDA-visible GPU exists
- Show GPU name
- Show VRAM total/free
- Warn if VRAM is below 24 GB
- Set:

```bash
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
OPENCV_IO_ENABLE_OPENEXR=1
```

The backend should include a GPU guard:

- Only run one TRELLIS generation job at a time by default.
- Queue extra jobs.
- Before generation, log VRAM usage.
- After generation, run:

```python
torch.cuda.empty_cache()
```

Do not run parallel jobs on one RTX 3090 unless the user explicitly enables unsafe mode.

---

### 5. Job System

Each generation creates a job folder:

```text
output/YYYY-MM-DD_HH-MM-SS_job-name/
├── input_original.ext
├── input_normalized.png
├── output.glb
├── preview.mp4
├── metadata.json
└── job.log
```

`metadata.json` should contain:

```json
{
  "app_name": "Trellis Local Studio",
  "model": "microsoft/TRELLIS.2-4B",
  "input_file": "input_normalized.png",
  "created_at": "ISO timestamp",
  "gpu": "NVIDIA GeForce RTX 3090",
  "settings": {
    "preset": "Balanced",
    "decimation_target": 1000000,
    "texture_size": 4096,
    "remesh": true,
    "remesh_band": 1,
    "remesh_project": 0,
    "extension_webp": true
  },
  "outputs": {
    "glb": "output.glb",
    "preview": "preview.mp4"
  }
}
```

---

## Backend API

Use FastAPI.

Required endpoints:

```text
GET  /
GET  /api/health
GET  /api/system
GET  /api/options
POST /api/jobs
GET  /api/jobs
GET  /api/jobs/{job_id}
GET  /api/jobs/{job_id}/download/glb
GET  /api/jobs/{job_id}/download/preview
GET  /api/jobs/{job_id}/log
```

Optional:

```text
POST /api/jobs/batch
POST /api/cache/clear
GET  /api/model/status
POST /api/model/preload
POST /api/model/unload
```

---

## Frontend Requirements

Keep the frontend simple and local.

The UI should include:

```text
Upload image
Quality preset dropdown
Advanced options collapsible panel
Generate button
Queue/status table
Progress/log view
Output file links
System/GPU info panel
```

No user accounts.

No remote calls except model download from Hugging Face during setup or first run.

No analytics.

---

## Engine Wrapper Requirements

Create an engine wrapper so the UI does not call TRELLIS.2 directly.

File:

```text
app/engine/trellis_engine.py
```

Responsibilities:

- Lazy-load TRELLIS.2 pipeline.
- Keep pipeline in GPU memory while app is running.
- Accept normalized PIL image.
- Run TRELLIS.2 generation.
- Export GLB.
- Optionally render preview video.
- Log all settings.
- Catch CUDA OOM errors and return helpful messages.
- Clean up GPU memory after job.

Pseudo-code:

```python
class TrellisEngine:
    def __init__(self, model_name="microsoft/TRELLIS.2-4B"):
        self.model_name = model_name
        self.pipeline = None

    def load(self):
        if self.pipeline is None:
            from trellis2.pipelines import Trellis2ImageTo3DPipeline
            self.pipeline = Trellis2ImageTo3DPipeline.from_pretrained(self.model_name)
            self.pipeline.cuda()

    def generate(self, image, export_options, job_dir):
        self.load()

        mesh = self.pipeline.run(image)[0]

        if hasattr(mesh, "simplify"):
            mesh.simplify(16777216)

        glb = export_to_glb(mesh, export_options)
        glb.export(str(job_dir / "output.glb"), extension_webp=export_options.extension_webp)

        return job_outputs
```

Important:

- Implement `export_to_glb` by following the official TRELLIS.2 example.
- Do not invent unsupported parameters for `pipeline.run`.
- Inspect actual installed function signatures and official `app.py` before exposing generation options beyond export settings.

---

## Official TRELLIS.2 Install Path

Create install script:

```text
scripts/install_trellis2.sh
```

Suggested content:

```bash
#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

sudo apt update
sudo apt install -y \
  git git-lfs wget curl build-essential cmake ninja-build \
  ffmpeg libgl1 libglib2.0-0

git lfs install

if [ ! -d "third_party/TRELLIS.2" ]; then
  mkdir -p third_party
  git clone -b main https://github.com/microsoft/TRELLIS.2.git --recursive third_party/TRELLIS.2
fi

cd third_party/TRELLIS.2

export CUDA_HOME="${CUDA_HOME:-/usr/local/cuda-12.4}"
export PATH="$CUDA_HOME/bin:$PATH"
export LD_LIBRARY_PATH="$CUDA_HOME/lib64:${LD_LIBRARY_PATH:-}"

. ./setup.sh --new-env --basic --flash-attn --nvdiffrast --nvdiffrec --cumesh --o-voxel --flexgemm

echo "TRELLIS.2 environment should now be installed."
echo "Activate with: conda activate trellis2"
```

Add a note in README:

```text
If Ubuntu 26 has CUDA/toolchain issues, install CUDA Toolkit 12.4 exactly and ensure CUDA_HOME=/usr/local/cuda-12.4 before running setup.
```

---

## App Dependency Install

Create:

```text
requirements-app.txt
```

Suggested content:

```text
fastapi
uvicorn[standard]
python-multipart
pillow
pydantic
aiofiles
jinja2
```

Install inside the same `trellis2` Conda environment after TRELLIS.2 setup:

```bash
conda activate trellis2
pip install -r requirements-app.txt
```

---

## Run Script

Create:

```text
scripts/run_app.sh
```

Suggested content:

```bash
#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

export OPENCV_IO_ENABLE_OPENEXR=1
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

export TRELLIS_LOCAL_HOST="${TRELLIS_LOCAL_HOST:-127.0.0.1}"
export TRELLIS_LOCAL_PORT="${TRELLIS_LOCAL_PORT:-7860}"

python -m uvicorn app.main:app \
  --host "$TRELLIS_LOCAL_HOST" \
  --port "$TRELLIS_LOCAL_PORT"
```

Default local URL:

```text
http://127.0.0.1:7860
```

---

## System Check Script

Create:

```text
scripts/check_gpu.sh
```

Suggested content:

```bash
#!/usr/bin/env bash
set -euo pipefail

echo "Checking NVIDIA GPU..."
nvidia-smi

echo
echo "Checking CUDA compiler..."
if command -v nvcc >/dev/null 2>&1; then
  nvcc --version
else
  echo "nvcc not found. CUDA Toolkit may not be installed or PATH is not set."
fi

echo
echo "Checking Python..."
python --version

echo
echo "Checking PyTorch CUDA..."
python - <<'PY'
import torch
print("torch:", torch.__version__)
print("cuda available:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("gpu:", torch.cuda.get_device_name(0))
    print("vram gb:", torch.cuda.get_device_properties(0).total_memory / 1024**3)
PY
```

---

## Error Handling Requirements

The app must show helpful errors for:

```text
CUDA out of memory
no NVIDIA GPU detected
model download missing/failing
invalid image
unsupported image format
GLB export failure
preview render failure
permission denied writing output
```

For CUDA OOM, suggest:

```text
Use Draft or Balanced preset
Lower decimation_target
Lower texture_size
Close other GPU apps
Restart the app to unload VRAM
```

---

## Batch Mode

Implement optional batch mode after single-image mode works.

Batch mode:

- User selects multiple images or an input folder.
- Jobs are queued one by one.
- Each image gets its own output folder.
- Failed jobs do not stop the whole batch.
- Summary report generated at the end:

```text
batch_summary.json
batch_summary.csv
```

---

## Front/Back Image Mode

Include this only as a clearly labeled experimental/organizational feature.

UI label:

```text
Front / Back Pair Mode
```

Rules:

1. Allow upload of front image and optional back image.
2. Let user choose the primary generation image:
   - front
   - back
3. Store both images in job folder.
4. Generate from the selected primary image only.
5. Add metadata noting both images were provided.
6. Do not claim TRELLIS.2 natively used both views unless a verified multi-view module is later implemented.

Future extension placeholder:

```text
TODO: optional texture projection/refinement from back image in Blender or a separate module.
```

---

## Security Requirements

Local-only by default:

```python
host = "127.0.0.1"
```

Do not:

```text
open firewall ports
bind to 0.0.0.0 by default
upload images externally
send telemetry
store secrets in repo
```

If LAN mode is added later, it must require explicit config:

```bash
TRELLIS_LOCAL_HOST=0.0.0.0
```

and print a warning.

---

## Performance Notes For RTX 3090

Default to one job at a time.

Expected behavior:

```text
512-ish / fast settings: more reliable
1024-ish / balanced export: normal target
1536-ish / max quality: may be slow or fail depending memory and implementation
```

Do not promise H100 timings on RTX 3090.

The app should log:

```text
GPU name
free VRAM before job
free VRAM after job
preset
export settings
generation duration
export duration
total duration
```

---

## Output Compatibility

Primary:

```text
.glb
```

Useful for:

```text
Blender
Unity
web viewers
game asset previews
```

Optional future exports:

```text
.obj
.fbx
.stl
.usdz
```

Do not implement extra formats until GLB is reliable.

For Unity:

- GLB may need importer package.
- FBX export can be added later via Blender automation.
- Include scale/origin cleanup later if needed.

For 3D printing:

- Warn that AI meshes may not be watertight.
- Add future optional mesh repair.
- Do not promise print-ready STL from raw TRELLIS output.

---

## README Requirements

Create README.md with:

1. What the app does
2. What it does not do
3. Hardware requirements
4. Ubuntu 26 notes
5. Install steps
6. Run steps
7. Preset explanation
8. Troubleshooting
9. Output folder explanation

README must clearly say:

```text
This app does image-to-3D only. It does not generate input images from text.
```



---

## Mandatory Visual Interface Requirements

Because the target system is **Ubuntu Desktop**, the app must include a proper visual interface. A command-line-only app is not acceptable as the final product.

The visual interface may be implemented as one of these options:

```text
Option A: Local web UI opened in the browser
Option B: Desktop wrapper around the local web UI using Tauri, Electron, PyWebView, or similar
Option C: Native Linux desktop UI using Qt/PySide6, GTK, or similar
```

Preferred implementation for first version:

```text
FastAPI backend + proper local browser UI
```

Optional later improvement:

```text
desktop launcher / .desktop file that opens the UI automatically
```

The UI must feel like an actual local application, not a raw developer test page.

---

## Visual Interface Scope

The interface must expose all important app functionality through buttons, forms, panels, status views, and clear labels.

The user should not need to manually run Python commands to generate a model after the app is installed.

The UI must include these main sections:

```text
Dashboard / Home
New Generation
Job Queue
Results / History
System / GPU Info
Settings
Logs / Troubleshooting
Help / Usage
```

---

## UI Layout Requirements

Use a clean desktop-friendly layout.

Recommended layout:

```text
Top bar:
  App name, model status, GPU status, settings button

Left sidebar:
  Dashboard
  New Generation
  Jobs
  Results
  Settings
  Help

Main panel:
  Current selected page

Bottom/status area:
  active job status, GPU memory summary, errors/warnings
```

The UI should work well at common desktop resolutions:

```text
1920x1080
2560x1440
3840x2160
```

It should be usable on a normal Ubuntu Desktop monitor without needing browser zoom tricks.

---

## Required UI Pages

### 1. Dashboard / Home Page

Must show:

```text
app status
TRELLIS.2 model loaded/not loaded
GPU name
VRAM total/free
CUDA status
current queue status
recent outputs
quick "New Generation" button
```

Also show clear warnings if:

```text
no GPU is detected
CUDA is not available
VRAM is below 24 GB
model is not downloaded
app is running in unsafe LAN mode
```

---

### 2. New Generation Page

This is the main working screen.

Must include:

```text
image upload area
drag-and-drop upload
image preview
input file details
generation mode selector
quality preset selector
advanced options panel
output name field
generate button
reset button
```

Supported generation modes in UI:

```text
Single Image
Front / Back Pair
Batch Folder / Multiple Images
```

The UI must clearly explain:

```text
TRELLIS.2 is single-image based.
For front/back pair mode, choose which image is the primary generation image.
The second image is saved for reference unless a verified multi-view/refinement module is later added.
```

For front/back pair mode, UI must include:

```text
front image upload
back image upload
primary image selector: front or back
preview both images side by side
clear note that this is not native image fusion
```

For batch mode, UI must include:

```text
multi-file upload
file list
remove individual file button
batch preset
start batch button
batch progress
```

---

### 3. Quality Preset UI

The UI must expose these presets:

```text
Draft / Fast
Balanced
High Quality
Experimental / Max
Custom
```

Each preset should display a short explanation:

```text
Draft / Fast: quick test, smaller output
Balanced: recommended for RTX 3090
High Quality: better output, slower/heavier
Experimental / Max: may fail or run out of VRAM
Custom: manually controlled settings
```

Changing preset should update visible advanced settings.

---

### 4. Advanced Options UI

The advanced options panel must include:

```text
decimation_target
texture_size
remesh
remesh_band
remesh_project
extension_webp
render_preview
preview_fps
preview_turntable_seconds
output_basename
```

Use proper controls:

```text
number inputs
sliders where useful
checkboxes/toggles
dropdowns for fixed values
tooltips/help text
validation warnings
```

For dangerous/high-memory settings, show a warning before generation.

Example warning:

```text
8192 texture size and very high decimation targets may exceed RTX 3090 VRAM. Use Balanced if generation fails.
```

---

### 5. Job Queue Page

Must show all jobs with:

```text
job name
input thumbnail
mode
preset
status
progress
created time
duration
output folder
error summary if failed
buttons: view, open output, download GLB, view log, retry, delete
```

Statuses:

```text
queued
loading_model
running
exporting
rendering_preview
completed
failed
cancelled
```

Only one TRELLIS generation job should run at a time by default.

The UI must show queue position for waiting jobs.

---

### 6. Results / History Page

Must show completed generations.

Each result card/table row should include:

```text
thumbnail
job name
preset
created time
GLB file link
preview link if available
metadata link
open output folder button
reuse settings button
delete button
```

The result page should make it easy to find previous generated models.

---

### 7. System / GPU Info Page

Must show:

```text
GPU name
driver version
CUDA availability
PyTorch version
total VRAM
free VRAM
used VRAM
current process VRAM if available
CUDA_HOME
Python version
Conda environment name
TRELLIS.2 repo path
model cache path
disk free space for output folder
```

Include buttons:

```text
refresh system info
preload model
unload model
clear CUDA cache
open logs folder
```

If unload/clear cache are implemented, they must be safe and documented.

---

### 8. Settings Page

Must include:

```text
default preset
output folder path
model cache path
max queued jobs
auto-load model on startup
auto-render preview
default texture size
default decimation target
local host/port display
LAN mode warning if enabled
theme: system/light/dark
```

Settings must be stored locally in a simple config file, for example:

```text
config.local.json
```

Do not store secrets.

Do not require a user account.

---

### 9. Logs / Troubleshooting Page

Must include:

```text
live app log viewer
selected job log viewer
copy log button
open log file button
common troubleshooting hints
```

The UI should show friendly explanations for common errors:

```text
CUDA out of memory
model not downloaded
invalid image
GLB export failed
preview render failed
```

---

### 10. Help / Usage Page

The app must include built-in usage help.

Must include:

```text
what the app does
what the app does not do
how to generate a model
how presets work
how front/back pair mode works
where files are saved
how to use output in Blender
how to use output in Unity
how to stop the app
known limitations
```

This page should mirror the content of `docs/USER_GUIDE.md` in shorter form.

---

## Visual Preview Requirements

The UI should include visual previews where practical:

```text
input image preview
front/back side-by-side preview
batch thumbnails
completed job thumbnail
preview video or turntable if available
basic 3D viewer if practical
```

Preferred:

```text
Use a browser-based GLB viewer such as model-viewer or Three.js if practical.
```

If a full 3D viewer is too much for the first version, the UI must still provide:

```text
download/open GLB link
preview video if generated
clear output folder link
```

Do not block core generation on a complex viewer. GLB generation is the priority.

---

## Desktop Integration Requirements

Because the target is Ubuntu Desktop, include optional desktop integration.

Create:

```text
scripts/create_desktop_launcher.sh
```

It should create a launcher similar to:

```text
~/.local/share/applications/trellis-local-studio.desktop
```

The launcher should:

```text
start the local app
open the browser to http://127.0.0.1:7860
use a clear app name
use a local icon if provided
```

Also include:

```text
scripts/stop_app.sh
```

Optional but useful:

```text
scripts/open_output_folder.sh
```

The README and USER_GUIDE must explain how to use the launcher.

---

## UI Quality Acceptance Criteria

The app is not complete unless:

1. A visual interface exists.
2. The visual interface can start a generation without manual Python commands.
3. The visual interface exposes all required generation modes.
4. The visual interface exposes all quality presets.
5. The visual interface exposes advanced export options.
6. The visual interface shows GPU/model/system status.
7. The visual interface shows job progress and job history.
8. The visual interface provides links/buttons to generated outputs.
9. The visual interface explains front/back limitations clearly.
10. The visual interface includes help/usage information.
11. The app includes Ubuntu Desktop launcher instructions or script.
12. The documentation includes screenshots or text descriptions of the UI pages once implemented.


---

## Multi-Agent Instruction File Compatibility

The project must be usable by multiple coding agents, including OpenAI Codex-style agents and Claude Code.

Maintain both instruction files:

```text
AGENTS.md
CLAUDE.md
```

### AGENTS.md

`AGENTS.md` is the main canonical project instruction file for this project.

It should contain the full detailed build specification, constraints, documentation requirements, UI requirements, and acceptance criteria.

OpenAI Codex-style agents are expected to read `AGENTS.md`.

### CLAUDE.md

Claude Code specifically uses `CLAUDE.md` files for project memory/instructions.

Create a root-level:

```text
CLAUDE.md
```

The `CLAUDE.md` file must either:

1. Contain the same complete instructions as `AGENTS.md`, or
2. Clearly instruct Claude to read and follow `AGENTS.md`.

Preferred lightweight `CLAUDE.md` content:

```markdown
# CLAUDE.md — Claude Code Instructions

This project uses `AGENTS.md` as the canonical build specification.

Before making changes, read and follow:

- `AGENTS.md`
- `README.md`
- `docs/BUILD_PROCESS.md`
- `docs/FUNCTIONALITY.md`
- `docs/USER_GUIDE.md`
- `docs/TROUBLESHOOTING.md`
- `docs/ARCHITECTURE.md`
- `docs/CHANGELOG.md`

The app goal is a standalone Ubuntu Desktop visual application for local TRELLIS.2 image-to-3D generation on an RTX 3090.

Important constraints:

- Image-to-3D only
- No integrated image creation
- No text-to-image
- No ComfyUI dependency
- Local-only by default
- Proper visual interface required
- Documentation must be updated during the build
- TRELLIS.2 is single-image based unless a verified multi-view module is later implemented
```

The agent must create or update `CLAUDE.md` whenever `AGENTS.md` changes in a way that affects Claude’s instructions.

### Do Not Assume Universal Support

Do not assume every AI coding assistant automatically reads `AGENTS.md`.

For compatibility, keep instruction files explicit:

```text
AGENTS.md     — canonical detailed spec
CLAUDE.md     — Claude Code entry point
README.md     — human/user entry point
```

If future agents require their own instruction filenames, add them only when needed and document them here.

---

## Multi-Agent Acceptance Criteria

The project is not complete unless:

1. `AGENTS.md` exists and contains the full canonical build instructions.
2. `CLAUDE.md` exists at the project root.
3. `CLAUDE.md` tells Claude Code to follow `AGENTS.md`.
4. `README.md` tells the human user that both instruction files exist.
5. Any major change to `AGENTS.md` is reflected in `CLAUDE.md` or its reference instructions.

---

## Mandatory Documentation Requirements

The coding agent must document the project while building it. Documentation is not optional and must be kept up to date as features are added or changed.

Create and maintain these files:

```text
README.md
docs/
├── BUILD_PROCESS.md
├── FUNCTIONALITY.md
├── USER_GUIDE.md
├── TROUBLESHOOTING.md
├── ARCHITECTURE.md
└── CHANGELOG.md
```

### README.md

The main `README.md` must be the starting point for the user.

It must include:

```text
what the app does
what the app does not do
hardware requirements
Ubuntu 26 Desktop notes
RTX 3090 / 24 GB VRAM notes
install summary
run summary
where outputs are saved
link to detailed docs
```

The README must clearly state:

```text
This app uses existing user-provided images as input.
This app does not create images from text prompts.
This app does not include integrated text-to-image generation.
```

### docs/BUILD_PROCESS.md

Document the full build process step by step.

This file must include:

```text
system preparation
NVIDIA driver check
CUDA Toolkit check
Conda/Mamba setup
TRELLIS.2 clone/install steps
Python environment setup
app dependency setup
model download/preload process
first test run
known Ubuntu 26 issues
known RTX 3090 limitations
commands used during installation
```

Every important command used by the agent during setup must be copied into this file.

If the agent changes a command because of an error, document:

```text
the failed command
the error summary
the fixed command
why the change was needed
```

### docs/FUNCTIONALITY.md

Document all app functionality.

This file must include:

```text
single-image generation
front/back pair mode behavior
batch mode behavior
quality presets
advanced export options
job queue behavior
GPU/memory handling
model preload/unload behavior
output folder structure
metadata/log generation
preview rendering if implemented
```

For every feature, include:

```text
feature name
what it does
what it does not do
user-facing controls
backend files involved
known limitations
```

The front/back feature must clearly say:

```text
TRELLIS.2 generation is single-image based.
Front/back pair mode stores both images and lets the user choose the primary image.
It does not mean both images are natively fused into one reconstruction unless a verified multi-view module is added later.
```

### docs/USER_GUIDE.md

Create beginner-friendly instructions for using the finished app.

This file must include:

```text
how to start the app
what URL to open
how to upload an image
how to choose a preset
how to use advanced options
how to generate a model
how to find the output GLB
how to open the GLB in Blender
how to use the output in Unity
how to run batch mode
how to use front/back pair mode
how to stop the app
```

Use simple language and step-by-step instructions.

Include example workflow:

```text
1. Start app
2. Open http://127.0.0.1:7860
3. Upload image
4. Choose Balanced
5. Click Generate
6. Wait for job to finish
7. Open output folder
8. Import output.glb into Blender
```

### docs/TROUBLESHOOTING.md

Document common problems and fixes.

Must include sections for:

```text
nvidia-smi not working
CUDA not found
PyTorch CUDA not available
CUDA out of memory
model download failure
Hugging Face access/cache problems
invalid image upload
GLB export failure
preview render failure
Ubuntu 26 dependency issue
Conda environment issue
app starts but page does not open
port already in use
```

For each issue, include:

```text
symptom
likely cause
commands to check
recommended fix
```

### docs/ARCHITECTURE.md

Document how the app is built internally.

Must include:

```text
folder structure
backend API overview
frontend overview
job queue design
TRELLIS.2 engine wrapper design
GPU guard design
output folder lifecycle
configuration/environment variables
security/local-only design
```

Also include a simple architecture diagram in text form:

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

### docs/CHANGELOG.md

Maintain a changelog as the project is built.

Use this format:

```text
# Changelog

## Unreleased

### Added
- ...

### Changed
- ...

### Fixed
- ...

### Known Issues
- ...
```

Every meaningful implementation step must update the changelog.

---

## Documentation Rules For The Agent

The agent must follow these rules:

1. Update documentation in the same commit/session as code changes.
2. Do not leave documentation until the end.
3. If a feature is incomplete, document it as incomplete.
4. If behavior differs from this `AGENTS.md`, document the reason.
5. If an install command fails and is replaced, document both the failure and the fix.
6. If Ubuntu 26 requires special handling, document it clearly.
7. If TRELLIS.2 upstream changes function signatures, document the discovered version-specific behavior.
8. The user guide must be understandable by a non-programmer.
9. The build process document must be detailed enough that the user can rebuild the app later.
10. Never document false functionality. If front/back mode is only organizational, say so.

---

## Documentation Acceptance Criteria

The project is not complete unless:

1. `README.md` exists and explains the app clearly.
2. `docs/BUILD_PROCESS.md` contains the actual build/install commands used.
3. `docs/FUNCTIONALITY.md` documents every implemented feature.
4. `docs/USER_GUIDE.md` explains how to use the app from start to finish.
5. `docs/TROUBLESHOOTING.md` includes common CUDA/GPU/install errors.
6. `docs/ARCHITECTURE.md` explains the internal app structure.
7. `docs/CHANGELOG.md` has entries for implemented work.
8. Documentation matches the current code behavior.
9. Documentation clearly says the app does not include integrated image generation.
10. Documentation clearly says TRELLIS.2 is single-image based unless a verified multi-view module is later added.

---

## Acceptance Criteria

The project is successful when:

1. `scripts/check_gpu.sh` detects RTX 3090 and PyTorch CUDA.
2. `scripts/run_app.sh` starts local web UI at `http://127.0.0.1:7860`.
3. User can upload a `.png` or `.jpg`.
4. User can select Draft/Balanced/High/Experimental preset.
5. App generates a `.glb`.
6. App saves metadata and logs.
7. App does not call any text-to-image/image-generation model.
8. App queues jobs instead of running multiple TRELLIS jobs at the same time.
9. App handles CUDA OOM gracefully.
10. App works without internet after model and dependencies are downloaded.
11. Documentation is created and updated during the build.
12. README.md explains what the app does, what it does not do, and how to start it.
13. docs/BUILD_PROCESS.md documents the actual commands and fixes used during setup.
14. docs/FUNCTIONALITY.md documents all implemented features and limitations.
15. docs/USER_GUIDE.md gives step-by-step usage instructions.
16. docs/TROUBLESHOOTING.md covers common CUDA, GPU, model, and app errors.
17. docs/ARCHITECTURE.md explains the app structure.
18. docs/CHANGELOG.md is updated with meaningful implementation changes.
19. A proper visual interface is implemented for Ubuntu Desktop use.
20. The UI exposes generation, presets, advanced options, queue, results, GPU/system info, logs, settings, and help.
21. Desktop launcher creation is documented or scripted.
22. Root-level CLAUDE.md is created so Claude Code can follow the project instructions.
23. CLAUDE.md clearly points Claude to AGENTS.md as the canonical spec.

---

## Development Order

Build in this order:

### Phase 1 — Environment

- Install system dependencies
- Clone official TRELLIS.2
- Install Conda environment
- Verify official `example.py` works

### Phase 2 — Minimal CLI

Create a local CLI wrapper:

```bash
python -m app.cli.generate \
  --input input/test.png \
  --preset balanced \
  --output output/test
```

CLI should generate GLB before web UI is built.

### Phase 3 — Web App

- FastAPI backend
- upload endpoint
- job queue
- simple web UI
- status/log view

### Phase 4 — Presets + Advanced Options

- Add preset dropdown
- Add advanced export options
- Add validation and warnings

### Phase 5 — Batch + Front/Back Pair Mode

- Batch jobs
- Paired front/back organization
- Metadata support

### Phase 6 — Polish

- Better preview
- Better logging
- Model preload/unload
- README screenshots
- optional `.desktop` launcher

---

## Do Not Do

Do not:

```text
add text-to-image
add prompt-to-image
use ComfyUI as a dependency
require cloud GPU
require remote server
make the app internet-facing
hardcode user-specific paths
run multiple RTX 3090 jobs in parallel by default
claim true multi-view support unless implemented and tested
claim print-ready mesh without repair
```

---

## Notes For The Coding Agent

Before coding against TRELLIS.2 internals:

1. Open official `example.py`.
2. Open official `app.py`.
3. Inspect `Trellis2ImageTo3DPipeline.run` signature.
4. Inspect `o_voxel.postprocess.to_glb` signature.
5. Only expose arguments that exist in the installed version.
6. Keep app-level options separate from model-level options.
7. Prefer safe defaults over maximum settings.

Where uncertain, implement a conservative wrapper and leave TODO comments instead of inventing behavior.

---

## Final Expected User Experience

The user starts the app:

```bash
./scripts/run_app.sh
```

Opens:

```text
http://127.0.0.1:7860
```

Uploads an image.

Chooses:

```text
Balanced
```

Clicks:

```text
Generate 3D Model
```

Gets:

```text
output.glb
preview.mp4
metadata.json
job.log
```

The app runs fully locally on Ubuntu Desktop with the RTX 3090 and does not include any image creation model.
