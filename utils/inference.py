"""Inference helpers for crop and production predictions."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from utils.config import CROP_FEATURE_COLUMNS, PRODUCTION_COLUMNS


def validate_crop_inputs(
    temperature: float,
    humidity: float,
    ph: float,
    rainfall: float,
) -> str | None:
    """Validate crop recommendation inputs and return an error message if invalid."""
    checks = [
        (not np.isfinite(temperature), "Temperature must be a valid number."),
        (not np.isfinite(humidity), "Humidity must be a valid number."),
        (not np.isfinite(ph), "pH must be a valid number."),
        (not np.isfinite(rainfall), "Rainfall must be a valid number."),
        (humidity < 0 or humidity > 100, "Humidity must be between 0 and 100."),
        (ph < 0 or ph > 14, "pH must be between 0 and 14."),
        (rainfall < 0, "Rainfall cannot be negative."),
    ]
    for is_invalid, message in checks:
        if is_invalid:
            return message
    return None


def predict_crop(
    artifact: dict[str, Any],
    label_encoder: Any,
    temperature: float,
    humidity: float,
    ph: float,
    rainfall: float,
) -> dict[str, Any]:
    """Run crop recommendation inference using saved artifacts."""
    error = validate_crop_inputs(temperature, humidity, ph, rainfall)
    if error:
        return {"error": error}

    features = pd.DataFrame(
        [{col: value for col, value in zip(CROP_FEATURE_COLUMNS, [temperature, humidity, ph, rainfall])}]
    )
    imputed = pd.DataFrame(
        artifact["imputer"].transform(features),
        columns=artifact["feature_columns"],
    )

    model = artifact["model"]
    prediction = model.predict(imputed)
    probabilities = model.predict_proba(imputed)[0]
    crop = label_encoder.inverse_transform(prediction.ravel())[0]
    confidence = float(np.max(probabilities))

    top_indices = np.argsort(probabilities)[::-1][:3]
    alternatives = [
        {
            "crop": label_encoder.inverse_transform([idx])[0],
            "confidence": float(probabilities[idx]),
        }
        for idx in top_indices
    ]

    return {
        "crop": crop,
        "confidence": confidence,
        "alternatives": alternatives,
    }


def validate_production_inputs(
    state: str,
    district: str,
    season: str,
    crop: str,
    area: float,
) -> str | None:
    """Validate production prediction inputs."""
    if not state:
        return "⚠ Please select all required inputs."
    if not district:
        return "⚠ Please select all required inputs."
    if not season:
        return "⚠ Please select all required inputs."
    if not crop:
        return "⚠ Please select all required inputs."
    if not np.isfinite(area) or area <= 0:
        return "⚠ Area must be a positive number."
    return None


def predict_production(
    model: Any,
    preprocessor: Any,
    state: str,
    district: str,
    crop_year: int,
    season: str,
    crop: str,
    area: float,
) -> dict[str, Any]:
    """Run production prediction inference using saved model artifacts."""
    error = validate_production_inputs(state, district, season, crop, area)
    if error:
        return {"error": error}

    if not np.isfinite(crop_year):
        return {"error": "⚠ Prediction unavailable."}

    row = pd.DataFrame(
        [
            {
                "State_Name": state,
                "District_Name": district,
                "Crop_Year": int(crop_year),
                "Season": season,
                "Crop": crop,
                "Area": float(area),
            }
        ]
    )

    try:
        features = preprocessor.transform(row)
        prediction = float(model.predict(features)[0])
    except Exception:
        return {"error": "⚠ Prediction unavailable."}

    if not np.isfinite(prediction):
        return {"error": "Model returned an invalid prediction. Try different inputs."}

    return {
        "production": max(prediction, 0.0),
        "inputs": row.iloc[0].to_dict(),
    }


def lookup_fertilizer(fertilizer_df: pd.DataFrame, crop_name: str) -> dict[str, Any]:
    """Lookup fertilizer recommendation for a crop name."""
    if not crop_name:
        return {"error": "Please select a crop."}

    matches = fertilizer_df[fertilizer_df["Crop"].str.lower() == crop_name.lower()]
    if matches.empty:
        partial = fertilizer_df[
            fertilizer_df["Crop"].str.contains(crop_name, case=False, na=False, regex=False)
        ]
        if partial.empty:
            return {"error": f"No fertilizer recommendation found for '{crop_name}'."}
        record = partial.iloc[0]
    else:
        record = matches.iloc[0]

    return {
        "crop": record["Crop"],
        "N": float(record["N"]),
        "P": float(record["P"]),
        "K": float(record["K"]),
        "pH": float(record["pH"]),
    }
