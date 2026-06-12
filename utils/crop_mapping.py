"""Map crop model labels to production and fertilizer dataset names."""

from __future__ import annotations

import pandas as pd

MODEL_TO_DISPLAY: dict[str, str] = {
    "apple": "Apple",
    "banana": "Banana",
    "blackgram": "Blackgram",
    "chickpea": "Chickpea",
    "coconut": "Coconut",
    "coffee": "Coffee",
    "cotton": "Cotton",
    "grapes": "Grapes",
    "jute": "Jute",
    "kidneybeans": "Kidney Bean",
    "lentil": "Lentil",
    "maize": "Maize",
    "mango": "Mango",
    "mothbeans": "Moth Bean",
    "mungbean": "Mung Bean",
    "muskmelon": "Muskmelon",
    "orange": "Orange",
    "papaya": "Papaya",
    "pigeonpeas": "Pigeon Pea",
    "pomegranate": "Pomegranate",
    "rice": "Rice",
    "watermelon": "Watermelon",
}

MODEL_TO_PRODUCTION_HINTS: dict[str, list[str]] = {
    "blackgram": ["Blackgram", "Black gram"],
    "chickpea": ["Chickpea", "Gram", "Bengal Gram"],
    "kidneybeans": ["Kidney Bean", "Rajmash"],
    "lentil": ["Lentil", "Masoor"],
    "mothbeans": ["Moth Bean", "Matki"],
    "mungbean": ["Mung Bean", "Green Gram", "Moong"],
    "pigeonpeas": ["Arhar/Tur", "Pigeon Pea", "Tur"],
    "muskmelon": ["Muskmelon", "Musk Melon"],
}


def display_crop(crop: str) -> str:
    """Return a human-readable crop name."""
    return MODEL_TO_DISPLAY.get(crop.lower(), crop.replace("_", " ").title())


def match_production_crop(
    model_crop: str,
    production_df: pd.DataFrame,
    state: str,
    district: str,
    season: str,
) -> str | None:
    """
    Find the best matching crop name in the production dataset for inference.
    """
    filtered = production_df[
        (production_df["State_Name"] == state)
        & (production_df["District_Name"] == district)
        & (production_df["Season"].str.strip() == season.strip())
    ]
    available = sorted(filtered["Crop"].dropna().unique().tolist())
    if not available:
        filtered = production_df[
            (production_df["State_Name"] == state)
            & (production_df["District_Name"] == district)
        ]
        available = sorted(filtered["Crop"].dropna().unique().tolist())

    if not available:
        return None

    normalized = model_crop.lower().replace(" ", "")
    for crop in available:
        if crop.lower().replace(" ", "") == normalized:
            return crop

    for hint in MODEL_TO_PRODUCTION_HINTS.get(model_crop.lower(), [display_crop(model_crop)]):
        for crop in available:
            if hint.lower() in crop.lower() or crop.lower() in hint.lower():
                return crop

    for crop in available:
        if normalized in crop.lower().replace(" ", "") or crop.lower().replace(" ", "") in normalized:
            return crop

    return None
