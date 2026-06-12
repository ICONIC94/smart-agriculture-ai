"""Enhanced fertilizer recommendations from NPK lookup data."""

from __future__ import annotations

from typing import Any

import pandas as pd

from utils.crop_mapping import display_crop
from utils.inference import lookup_fertilizer


def _select_fertilizers(n: float, p: float, k: float) -> tuple[str, str]:
    """Choose primary and alternative fertilizers based on dominant nutrient needs."""
    nutrients = {"N": n, "P": p, "K": k}
    dominant = max(nutrients, key=nutrients.get)

    if dominant == "N":
        return "Urea", "DAP" if p >= k else "MOP (Muriate of Potash)"
    if dominant == "P":
        return "DAP", "Urea"
    return "MOP (Muriate of Potash)", "Urea"


def _application_timing(crop_name: str) -> str:
    """Return crop-aware fertilizer application guidance."""
    crop = crop_name.lower()
    if crop in {"rice", "wheat", "maize", "jowar", "bajra"}:
        return (
            "Apply a basal dose at sowing/transplanting, followed by split top-dressing "
            "during tillering and panicle/grain formation."
        )
    if crop in {"cotton", "sugarcane", "banana"}:
        return "Apply in split doses during vegetative and flowering stages for sustained growth."
    if crop in {"pulses", "lentil", "chickpea", "pigeonpeas", "mungbean", "blackgram"}:
        return "Apply phosphorus at sowing and nitrogen sparingly during early vegetative stage."
    return "Apply during the vegetative growth stage for optimal productivity."


def _build_guidance(crop: str, n: float, p: float, k: float, ph: float) -> str:
    """Generate practical fertilizer guidance text."""
    return (
        f"Maintain soil pH near {ph:.1f}. "
        f"Target nutrient application of N={n:.0f}, P={p:.0f}, K={k:.0f} kg/ha based on "
        f"crop-specific requirements for {display_crop(crop)}."
    )


def get_fertilizer_advice(fertilizer_df: pd.DataFrame, crop_name: str) -> dict[str, Any]:
    """
    Build a rich fertilizer recommendation from Fertilizer.csv lookup data.
    """
    lookup = lookup_fertilizer(fertilizer_df, crop_name)
    if "error" in lookup:
        return lookup

    primary, alternative = _select_fertilizers(lookup["N"], lookup["P"], lookup["K"])
    crop_key = crop_name.lower().replace(" ", "")

    return {
        "crop": lookup["crop"],
        "primary_fertilizer": primary,
        "alternative_fertilizer": alternative,
        "application_timing": _application_timing(crop_key),
        "guidance": _build_guidance(crop_name, lookup["N"], lookup["P"], lookup["K"], lookup["pH"]),
        "N": lookup["N"],
        "P": lookup["P"],
        "K": lookup["K"],
        "pH": lookup["pH"],
    }
