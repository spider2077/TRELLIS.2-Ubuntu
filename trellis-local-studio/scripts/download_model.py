#!/usr/bin/env python3
# Script: download_model.py
# Location: trellis-local-studio/scripts/download_model.py
"""Download the default TRELLIS.2 model into the local Hugging Face cache."""

from __future__ import annotations

import os


MODEL_NAME = os.environ.get("TRELLIS_MODEL_NAME", "microsoft/TRELLIS.2-4B")


def main() -> None:
    try:
        from huggingface_hub import snapshot_download
    except Exception as exc:
        raise SystemExit(
            "huggingface_hub is not installed. Install TRELLIS.2 dependencies first."
        ) from exc

    path = snapshot_download(MODEL_NAME)
    print(f"Downloaded {MODEL_NAME} to {path}")


if __name__ == "__main__":
    main()

