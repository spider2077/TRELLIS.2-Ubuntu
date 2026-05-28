"""CLI entry point for single-image TRELLIS.2 generation."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from app.config import APP_NAME, ensure_directories, settings
from app.engine.export_options import build_export_options
from app.engine.trellis_engine import TrellisEngine
from app.utils.image_prep import normalize_image
from app.utils.system_info import nvidia_smi_info


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a GLB from one image with TRELLIS.2.")
    parser.add_argument("--input", required=True, type=Path, help="Input image path.")
    parser.add_argument("--output", required=True, type=Path, help="Output job folder.")
    parser.add_argument("--preset", default="balanced", help="draft, balanced, high, experimental, or custom.")
    parser.add_argument("--decimation-target", type=int)
    parser.add_argument("--texture-size", type=int)
    parser.add_argument("--no-preview", action="store_true", help="Skip preview video rendering.")
    return parser.parse_args()


def main() -> None:
    ensure_directories()
    args = parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    normalized = args.output / "input_normalized.png"
    image_info = normalize_image(args.input, normalized)

    options = build_export_options(
        preset=args.preset,
        output_basename="output",
        decimation_target=args.decimation_target,
        texture_size=args.texture_size,
        render_preview=not args.no_preview,
    )
    metadata = {
        "app_name": APP_NAME,
        "model": settings.model_name,
        "input_file": normalized.name,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "gpu": nvidia_smi_info(),
        "settings": options.to_dict(),
        "image_info": image_info,
        "outputs": {"glb": None, "preview": None},
    }
    log_path = args.output / "job.log"

    def log(message: str) -> None:
        print(message)
        with log_path.open("a", encoding="utf-8") as log_file:
            log_file.write(f"{message}\n")

    outputs = TrellisEngine(model_name=settings.model_name).generate(normalized, args.output, options, metadata, log)
    print(json.dumps({"glb": str(outputs.glb), "preview": str(outputs.preview) if outputs.preview else None}, indent=2))


if __name__ == "__main__":
    main()

