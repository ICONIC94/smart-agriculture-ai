"""End-to-end farm analysis orchestration."""

from __future__ import annotations

from typing import Any

import pandas as pd

from utils.crop_mapping import display_crop, match_production_crop
from utils.loaders import get_reference_crop_year
from utils.explanation import generate_explanation
from utils.fertilizer_advice import get_fertilizer_advice
from utils.inference import predict_crop, predict_production
from utils.season import detect_season
from utils.weather import fetch_live_weather


def _format_alternatives(alternatives: list[dict[str, Any]], recommended: str) -> list[dict[str, Any]]:
    """Return top 3 alternative crops excluding the recommended crop."""
    filtered = [alt for alt in alternatives if alt["crop"].lower() != recommended.lower()]
    return [
        {
            "crop": display_crop(alt["crop"]),
            "confidence_pct": round(alt["confidence"] * 100, 1),
        }
        for alt in filtered[:3]
    ]


def _format_production(production: float, area: float) -> dict[str, float]:
    """Format production values for farmer-friendly display."""
    production = max(production, 0.0)
    yield_per_ha = production / area if area > 0 else 0.0
    return {
        "production_tonnes": round(production, 1),
        "yield_per_hectare": round(yield_per_ha, 2),
        "area_hectares": area,
    }


def analyze_farm(
    *,
    state: str,
    district: str,
    area: float,
    soil_ph: float,
    crop_artifact: dict[str, Any],
    label_encoder: Any,
    production_model: Any,
    production_preprocessor: Any,
    production_df: pd.DataFrame,
    fertilizer_df: pd.DataFrame,
    manual_weather: dict[str, float] | None = None,
) -> dict[str, Any]:
    """
    Run the complete farm analysis pipeline from location inputs to full report.
    """
    warnings: list[str] = []
    season_info = detect_season()

    if not state or not district:
        return {"error": "⚠ Please select all required inputs."}
    if area <= 0:
        return {"error": "⚠ Land area must be greater than zero."}

    weather: dict[str, Any]
    weather_manual = False

    if manual_weather:
        weather = {
            "temperature": manual_weather["temperature"],
            "humidity": manual_weather["humidity"],
            "rainfall": manual_weather["rainfall"],
            "rainfall_display": manual_weather["rainfall"],
            "condition": "Manual entry",
            "wind_speed": manual_weather.get("wind_speed", 0.0),
            "source": "Manual input",
            "success": True,
        }
        weather_manual = True
    else:
        weather_result = fetch_live_weather(state, district)
        if "error" in weather_result:
            return {
                "error": weather_result["error"],
                "needs_manual_weather": True,
                "season": season_info,
                "location": {"state": state, "district": district},
            }
        weather = weather_result

    crop_result = predict_crop(
        crop_artifact,
        label_encoder,
        weather["temperature"],
        weather["humidity"],
        soil_ph,
        weather["rainfall"],
    )
    if "error" in crop_result:
        return {"error": crop_result["error"]}

    recommended_crop = crop_result["crop"]
    crop_display = display_crop(recommended_crop)
    alternatives = _format_alternatives(crop_result["alternatives"], recommended_crop)

    production_crop = match_production_crop(
        recommended_crop,
        production_df,
        state,
        district,
        season_info["season"],
    )

    production_data: dict[str, Any] = {
        "production_tonnes": None,
        "yield_per_hectare": None,
        "area_hectares": area,
        "matched_crop": production_crop,
        "available": False,
    }

    if production_crop:
        reference_year = get_reference_crop_year(
            production_df,
            state,
            district,
            season_info["season"],
            production_crop,
        )
        prod_result = predict_production(
            production_model,
            production_preprocessor,
            state,
            district,
            reference_year,
            season_info["season"],
            production_crop,
            area,
        )
        if "error" in prod_result:
            warnings.append(f"Production forecast unavailable: {prod_result['error']}")
        else:
            production_data = {**_format_production(prod_result["production"], area), "available": True}
            production_data["matched_crop"] = production_crop
    else:
        warnings.append(
            f"No matching '{crop_display}' entry found for {district}, {state} "
            f"in the {season_info['season']} season. Production estimate skipped."
        )

    fertilizer = get_fertilizer_advice(fertilizer_df, recommended_crop)
    if "error" in fertilizer:
        warnings.append(fertilizer["error"])
        fertilizer = {}

    report: dict[str, Any] = {
        "location": {"state": state, "district": district},
        "soil_ph": soil_ph,
        "season": season_info,
        "weather": weather,
        "weather_manual": weather_manual,
        "crop": {
            "name": recommended_crop,
            "display_name": crop_display,
            "confidence_pct": round(crop_result["confidence"] * 100, 1),
            "alternatives": alternatives,
        },
        "production": production_data,
        "fertilizer": fertilizer,
        "warnings": warnings,
    }

    report["explanation"] = generate_explanation(report)
    return report
