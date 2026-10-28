"""Pironman enclosure model identification (independent of Home Assistant)."""
from __future__ import annotations

from collections.abc import Mapping

MODEL_NAMES = {
    "base": "Pironman 5",
    "mini": "Pironman 5 Mini",
    "max": "Pironman 5 Max",
    "pro_max": "Pironman 5 Pro Max",
}

MODEL_IDS = {
    "pironman5": "base",
    "pironman5-mini": "mini",
    "pironman5-max": "max",
    "pironman5-pro-max": "pro_max",
}

CONF_MODEL = "model"
AUTO = "auto"


def normalize_model(value: object) -> str | None:
    """Normalize explicit vendor model variants; never guess from peripheral presence."""
    if not isinstance(value, str):
        return None
    key = value.strip().casefold().replace("_", "-")
    if key in MODEL_IDS:
        return MODEL_IDS[key]
    if key in ("base", "mini", "max", "pro-max"):
        return "pro_max" if key == "pro-max" else key
    names = {name.casefold(): key for key, name in MODEL_NAMES.items()}
    return names.get(key)


def detect_model(info: Mapping | None) -> str | None:
    """Detect from explicit API metadata, returning None when ambiguous.

    A vendor-supplied generic `name=Pironman 5` is NOT sufficient evidence
    for the base model: older firmware may report that for every variant.
    """
    if not isinstance(info, Mapping):
        return None
    for key in ("id", "variant", "model_id", "product_id", "product", "model"):
        result = normalize_model(info.get(key))
        if result is not None:
            return result
    name = info.get("name")
    result = normalize_model(name)
    return result if result != "base" else None


def resolve_model(info: Mapping | None, selection: str = AUTO) -> tuple[str | None, str]:
    """Return (model, detection source). A manual selection always wins."""
    if selection != AUTO:
        model = normalize_model(selection)
        if model is None:
            raise ValueError(f"Unsupported model: {selection}")
        return model, "manual"
    detected = detect_model(info)
    return detected, "automatic" if detected else "unknown"
