#!/usr/bin/env python3
# Script: convert_glb_for_blender.py
# Location: trellis-local-studio/scripts/convert_glb_for_blender.py
"""Convert a WebP-textured GLB to PNG/JPEG textures for Blender import."""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Rewrite a GLB that uses EXT_texture_webp into a Blender-friendly GLB "
            "with embedded PNG textures."
        )
    )
    parser.add_argument("input_glb", type=Path, help="Source GLB path.")
    parser.add_argument(
        "output_glb",
        type=Path,
        nargs="?",
        help="Destination GLB path. Default: <name>_blender.glb beside the input.",
    )
    args = parser.parse_args()

    src = args.input_glb.expanduser().resolve()
    if not src.is_file():
        raise SystemExit(f"Input GLB not found: {src}")

    dst = args.output_glb
    if dst is None:
        dst = src.with_name(f"{src.stem}_blender.glb")
    else:
        dst = dst.expanduser().resolve()

    try:
        import trimesh
    except Exception as exc:
        raise SystemExit(
            "trimesh is not installed. Activate the trellis2 environment first."
        ) from exc

    scene = trimesh.load(str(src), force="scene")
    scene.export(str(dst), extension_webp=False)
    print(f"Wrote Blender-friendly GLB: {dst}")
    print("Import this file in Blender with File > Import > glTF 2.0 (.glb/.gltf).")


if __name__ == "__main__":
    main()
