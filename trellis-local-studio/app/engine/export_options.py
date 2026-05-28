"""Export presets and validation for Trellis Local Studio."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Any


TEXTURE_SIZES = {1024, 2048, 4096, 8192}
MIN_DECIMATION_TARGET = 50_000
MAX_DECIMATION_TARGET = 8_000_000


@dataclass(frozen=True)
class ExportOptions:
    """GLB export and optional preview settings."""

    preset: str = "balanced"
    decimation_target: int = 1_000_000
    texture_size: int = 4096
    remesh: bool = True
    remesh_band: int = 1
    remesh_project: float = 0
    extension_webp: bool = True
    render_preview: bool = True
    preview_fps: int = 15
    preview_turntable_seconds: int = 6
    output_basename: str = "output"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


PRESETS: dict[str, ExportOptions] = {
    "draft": ExportOptions(
        preset="draft",
        decimation_target=250_000,
        texture_size=2048,
        render_preview=False,
    ),
    "balanced": ExportOptions(preset="balanced"),
    "high": ExportOptions(
        preset="high",
        decimation_target=2_000_000,
        texture_size=4096,
    ),
    "experimental": ExportOptions(
        preset="experimental",
        decimation_target=4_000_000,
        texture_size=8192,
    ),
}

PRESET_LABELS = {
    "draft": "Draft / Fast",
    "balanced": "Balanced",
    "high": "High Quality",
    "experimental": "Experimental / Max",
    "custom": "Custom",
}

PRESET_DESCRIPTIONS = {
    "draft": "Quick test, smaller output.",
    "balanced": "Recommended default for RTX 3090.",
    "high": "Better output, slower and heavier.",
    "experimental": "Maximum settings; may fail or run out of VRAM.",
    "custom": "Manual export settings.",
}


def coerce_bool(value: Any, default: bool) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def build_export_options(preset: str = "balanced", **overrides: Any) -> ExportOptions:
    """Create validated export options from a preset plus user overrides."""

    preset_key = (preset or "balanced").strip().lower()
    base = PRESETS.get(preset_key, PRESETS["balanced"])
    options = replace(base, preset=preset_key if preset_key in PRESETS else "balanced")

    typed_overrides: dict[str, Any] = {}
    for key, value in overrides.items():
        if value in (None, ""):
            continue
        if key in {"decimation_target", "texture_size", "remesh_band", "preview_fps", "preview_turntable_seconds"}:
            typed_overrides[key] = int(value)
        elif key == "remesh_project":
            typed_overrides[key] = float(value)
        elif key in {"remesh", "extension_webp", "render_preview"}:
            typed_overrides[key] = coerce_bool(value, getattr(options, key))
        elif key == "output_basename":
            typed_overrides[key] = str(value).strip() or options.output_basename

    if typed_overrides:
        options = replace(options, preset="custom" if preset_key == "custom" else options.preset, **typed_overrides)

    errors = validate_export_options(options)
    if errors:
        raise ValueError("; ".join(errors))
    return options


def validate_export_options(options: ExportOptions) -> list[str]:
    errors: list[str] = []
    if not MIN_DECIMATION_TARGET <= options.decimation_target <= MAX_DECIMATION_TARGET:
        errors.append("decimation_target must be between 50,000 and 8,000,000")
    if options.texture_size not in TEXTURE_SIZES:
        errors.append("texture_size must be one of 1024, 2048, 4096, or 8192")
    if options.remesh_band < 0:
        errors.append("remesh_band must be zero or greater")
    if not 10 <= options.preview_fps <= 30:
        errors.append("preview_fps must be between 10 and 30")
    if not 3 <= options.preview_turntable_seconds <= 20:
        errors.append("preview_turntable_seconds must be between 3 and 20")
    return errors


def options_payload() -> dict[str, Any]:
    return {
        "presets": [
            {
                "key": key,
                "label": PRESET_LABELS[key],
                "description": PRESET_DESCRIPTIONS[key],
                "options": value.to_dict(),
            }
            for key, value in PRESETS.items()
        ]
        + [
            {
                "key": "custom",
                "label": PRESET_LABELS["custom"],
                "description": PRESET_DESCRIPTIONS["custom"],
                "options": PRESETS["balanced"].to_dict() | {"preset": "custom"},
            }
        ],
        "limits": {
            "decimation_target": [MIN_DECIMATION_TARGET, MAX_DECIMATION_TARGET],
            "texture_size": sorted(TEXTURE_SIZES),
            "preview_fps": [10, 30],
            "preview_turntable_seconds": [3, 20],
        },
    }

