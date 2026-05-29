# User Guide

## Start the App

First-time setup and run:

```bash
cd trellis-local-studio
./scripts/bootstrap_local.sh --run
```

After setup is complete, start the app later with:

```bash
cd trellis-local-studio
source "$HOME/miniforge3/etc/profile.d/conda.sh"
conda activate trellis2
./scripts/run_app.sh
```

Open:

```text
http://127.0.0.1:7860
```

## Generate a Model

1. Open the New Generation page.
2. Upload an existing `.png`, `.jpg`, `.jpeg`, or `.webp` image.
3. Choose a preset. Use Balanced for normal RTX 3090 use, or **High Quality** for mesh detail closest to the official demo.
4. Set **Generation resolution** to **1536** when you want maximum mesh detail (uses more VRAM and time than 1024).
5. Open Advanced export options only if you want to change GLB export settings.
6. Click Generate 3D Model.
7. Open the Job Queue page and wait for the job to finish.
8. Download `output.glb` from the completed job.

Example workflow:

1. Start app.
2. Open `http://127.0.0.1:7860`.
3. Upload image.
4. Choose Balanced.
5. Click Generate.
6. Wait for job to finish.
7. Open output folder.
8. Import `output.glb` into Blender.

## Presets

Presets control **both** TRELLIS.2 generation resolution and GLB export settings:

- Draft / Fast: **512** generation, quick tests.
- Balanced: **1024 cascade** generation; recommended starting point for RTX 3090.
- High Quality: **1536 cascade** generation plus 4096 export textures; closest to official demo mesh detail.
- Experimental / Max: **1536 cascade** with maximum export settings; may run out of VRAM.
- Custom: manually controlled generation and export settings.

## Generation Resolution vs Export Quality

The official TRELLIS.2 demo exposes **512 / 1024 / 1536** generation resolution. This controls mesh detail during inference (`512`, `1024_cascade`, `1536_cascade`).

Separate from that, **texture size** and **decimation target** control the exported GLB file. A job can use 1536 generation with a lower export texture size, or 1024 generation with 4096 textures.

For demo-like results:

1. Use **High Quality** or set generation resolution to **1536**.
2. Prefer a clean input PNG with a transparent background and a centered subject.
3. Leave **Use WebP extension** off for Blender.

## Advanced Options

Advanced options control GLB export size and preview behavior:

- generation resolution (512 / 1024 / 1536)
- decimation target
- texture size
- remesh settings
- WebP texture extension
- preview video settings
- output basename

If generation fails with CUDA out-of-memory, choose Draft or Balanced, lower generation resolution (1536 → 1024), and lower texture size or decimation target.

## Front / Back Pair Mode

Front/back pair mode is organizational.

1. Upload a front image.
2. Optionally upload a back image.
3. Choose whether the front or back image is the primary generation image.
4. Generate.

TRELLIS.2 generation is single-image based. The app does not natively fuse both images into one reconstruction.

## Batch Mode

1. Choose Batch Folder / Multiple Images.
2. Select multiple image files.
3. Choose a preset.
4. Click Generate 3D Model.

The app queues one job for each selected image.

## Find Outputs

Outputs are saved under:

```text
trellis-local-studio/output/
```

Each job folder includes a GLB, metadata, job log, and possibly a preview video.

## Open in Blender

TRELLIS.2 embeds textures **inside** the `.glb` file. You will not see separate `.png` or
material files in the job folder unless you export them yourself later.

For Blender compatibility:

1. In Trellis Local Studio, leave **Use WebP extension** turned **off** when generating.
2. Import the generated `.glb` with File > Import > glTF 2.0 (.glb/.gltf).

If you already generated a GLB with WebP enabled, convert it without re-running TRELLIS.2:

```bash
cd trellis-local-studio
source "$HOME/miniforge3/etc/profile.d/conda.sh"
conda activate trellis2
python scripts/convert_glb_for_blender.py \
  "output/YOUR_JOB_FOLDER/your-model.glb"
```

That writes `your-model_blender.glb` with PNG textures Blender can read.

In Blender:

1. Choose File > Import.
2. Select GLTF 2.0 / GLB.
3. Pick the Blender-friendly `.glb` (or a new export with WebP disabled).

## Use in Unity

Unity may need a GLB importer package. Import the generated `output.glb` with your chosen GLB importer and check scale/materials after import.

## Stop the App

Press `Ctrl+C` in the terminal running `run_app.sh`, or run:

```bash
cd trellis-local-studio
./scripts/stop_app.sh
```

