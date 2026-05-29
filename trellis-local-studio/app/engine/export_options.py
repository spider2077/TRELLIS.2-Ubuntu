"""Export presets and validation for Trellis Local Studio."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Any


TEXTURE_SIZES = {1024, 2048, 4096, 8192}
GENERATION_RESOLUTIONS = {512, 1024, 1536}
MIN_DECIMATION_TARGET = 50_000
MAX_DECIMATION_TARGET = 8_000_000

PIPELINE_TYPE_BY_RESOLUTION = {
    512: "512",
    1024: "1024_cascade",
    1536: "1536_cascade",
}


def pipeline_type_for_resolution(resolution: int) -> str:
    """Map UI resolution to the official TRELLIS.2 pipeline_type value."""

    try:
        return PIPELINE_TYPE_BY_RESOLUTION[int(resolution)]
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("pipeline_resolution must be one of 512, 1024, or 1536") from exc


@dataclass(frozen=True)
class ExportOptions:
    """Generation, GLB export, and optional preview settings."""

    preset: str = "balanced"
    pipeline_resolution: int = 1024
    decimation_target: int = 1_000_000
    texture_size: int = 4096
    remesh: bool = True
    remesh_band: int = 1
    remesh_project: float = 0
    extension_webp: bool = False
    render_preview: bool = True
    preview_fps: int = 15
    preview_turntable_seconds: int = 6
    output_basename: str = "output"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


PRESETS: dict[str, ExportOptions] = {
    "draft": ExportOptions(
        preset="draft",
        pipeline_resolution=512,
        decimation_target=250_000,
        texture_size=2048,
        render_preview=False,
    ),
    "balanced": ExportOptions(preset="balanced", pipeline_resolution=1024),
    "high": ExportOptions(
        preset="high",
        pipeline_resolution=1536,
        decimation_target=2_000_000,
        texture_size=4096,
    ),
    "experimental": ExportOptions(
        preset="experimental",
        pipeline_resolution=1536,
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
    "draft": "512 mesh generation for quick tests.",
    "balanced": "1024 cascade generation; recommended default for RTX 3090.",
    "high": "1536 cascade generation plus 4096 export textures; closest to official demo mesh detail.",
    "experimental": "1536 cascade with maximum export settings; may fail or run out of VRAM.",
    "custom": "Manual generation and export settings.",
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
    if preset_key == "custom":
        options = replace(base, preset="custom")
    else:
        options = replace(base, preset=preset_key if preset_key in PRESETS else "balanced")

    typed_overrides: dict[str, Any] = {}
    for key, value in overrides.items():
        if value in (None, ""):
            continue
        if key in {
            "pipeline_resolution",
            "decimation_target",
            "texture_size",
            "remesh_band",
            "preview_fps",
            "preview_turntable_seconds",
        }:
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
    if options.pipeline_resolution not in GENERATION_RESOLUTIONS:
        errors.append("pipeline_resolution must be one of 512, 1024, or 1536")
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
            "pipeline_resolution": sorted(GENERATION_RESOLUTIONS),
            "decimation_target": [MIN_DECIMATION_TARGET, MAX_DECIMATION_TARGET],
            "texture_size": sorted(TEXTURE_SIZES),
            "preview_fps": [10, 30],
            "preview_turntable_seconds": [3, 20],
        },
    }

