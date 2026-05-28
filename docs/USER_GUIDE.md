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
3. Choose a preset. Use Balanced for normal RTX 3090 use.
4. Open Advanced export options only if you want to change GLB settings.
5. Click Generate 3D Model.
6. Open the Job Queue page and wait for the job to finish.
7. Download `output.glb` from the completed job.

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

- Draft / Fast: quicker tests, smaller output.
- Balanced: recommended starting point for RTX 3090.
- High Quality: heavier export settings.
- Experimental / Max: may run out of VRAM.
- Custom: manually controlled settings.

## Advanced Options

Advanced options control GLB export size and preview behavior:

- decimation target
- texture size
- remesh settings
- WebP texture extension
- preview video settings
- output basename

If generation fails with CUDA out-of-memory, choose Draft or Balanced and lower texture size or decimation target.

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

In Blender:

1. Choose File > Import.
2. Select GLTF 2.0 / GLB.
3. Pick the generated `output.glb`.

## Use in Unity

Unity may need a GLB importer package. Import the generated `output.glb` with your chosen GLB importer and check scale/materials after import.

## Stop the App

Press `Ctrl+C` in the terminal running `run_app.sh`, or run:

```bash
cd trellis-local-studio
./scripts/stop_app.sh
```

