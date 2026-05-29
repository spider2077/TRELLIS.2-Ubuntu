#!/usr/bin/env python3
# Script: download_model.py
# Location: trellis-local-studio/scripts/download_model.py
"""Download TRELLIS.2 and its gated Hugging Face dependencies."""

from __future__ import annotations

import os
import sys
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP_ROOT))

MODEL_NAME = os.environ.get("TRELLIS_MODEL_NAME", "microsoft/TRELLIS.2-4B")
DINOV3_MODEL = "facebook/dinov3-vitl16-pretrain-lvd1689m"
RMBG_MODEL = "briaai/RMBG-2.0"


def main() -> None:
    from app.utils.huggingface_auth import check_huggingface_auth, format_huggingface_setup_help

    status = check_huggingface_auth()
    if not status.ready:
        print(format_huggingface_setup_help())
        raise SystemExit(
            "Hugging Face login or gated-model access is missing. "
            "Run ./scripts/setup_huggingface.sh first."
        )

    try:
        from huggingface_hub import snapshot_download
        from transformers import AutoModelForImageSegmentation, DINOv3ViTModel
    except Exception as exc:
        raise SystemExit(
            "Required packages are missing. Activate trellis2 and install TRELLIS.2 dependencies first."
        ) from exc

    print(f"Downloading {MODEL_NAME}...")
    trellis_path = snapshot_download(MODEL_NAME)
    print(f"Downloaded {MODEL_NAME} to {trellis_path}")

    print(f"Downloading gated dependency {DINOV3_MODEL}...")
    DINOv3ViTModel.from_pretrained(DINOV3_MODEL)
    print(f"DINOv3 weights cached for {DINOV3_MODEL}")

    print(f"Downloading gated dependency {RMBG_MODEL}...")
    AutoModelForImageSegmentation.from_pretrained(RMBG_MODEL, trust_remote_code=True)
    print(f"RMBG weights cached for {RMBG_MODEL}")

    print("Model download complete.")


if __name__ == "__main__":
    main()

