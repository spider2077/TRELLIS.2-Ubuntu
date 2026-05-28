"""Input image validation and normalization."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, UnidentifiedImageError


SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


class InvalidImageError(ValueError):
    """Raised when an uploaded image cannot be used for generation."""


def validate_image_path(path: Path) -> None:
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        raise InvalidImageError("Unsupported image format. Use PNG, JPG, JPEG, or WEBP.")


def normalize_image(source: Path, destination: Path) -> dict[str, object]:
    """Normalize an uploaded image without modifying the original file."""

    validate_image_path(source)
    try:
        with Image.open(source) as image:
            original_mode = image.mode
            has_alpha = image.mode in {"RGBA", "LA"} or (
                image.mode == "P" and "transparency" in image.info
            )
            normalized = image.convert("RGBA" if has_alpha else "RGB")
            destination.parent.mkdir(parents=True, exist_ok=True)
            normalized.save(destination, format="PNG")
            return {
                "width": normalized.width,
                "height": normalized.height,
                "mode": normalized.mode,
                "original_mode": original_mode,
                "has_alpha": has_alpha,
            }
    except UnidentifiedImageError as exc:
        raise InvalidImageError("Invalid image upload. PIL could not identify the file.") from exc

