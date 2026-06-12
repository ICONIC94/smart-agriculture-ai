"""Natural-language farm analysis explanations."""

from __future__ import annotations

from typing import Any


def _format_tonnes(value: float) -> str:
    """Format production as tonnes with commas."""
    if value >= 1_000_000:
        return f"{value / 1_000_000:,.2f} million tonnes"
    if value >= 1_000:
        return f"{value / 1_000:,.1f} thousand tonnes"
    return f"{value:,.0f} tonnes"


def generate_explanation(report: dict[str, Any]) -> str:
    """Generate a readable AI-style farming explanation from the analysis report."""
    location = report["location"]
    crop = report["crop"]["display_name"]
    confidence = report["crop"]["confidence_pct"]
    area = report["production"]["area_hectares"]
    production = report["production"].get("production_tonnes")
    yield_per_ha = report["production"].get("yield_per_hectare")
    season = report["season"]["season"]
    weather = report["weather"]
    fertilizer = report.get("fertilizer", {})

    weather_clause = (
        f"current weather conditions in {location['district']}, {location['state']} "
        f"({weather['temperature']}°C, {weather['humidity']}% humidity, "
        f"{weather.get('condition', 'moderate conditions')})"
    )

    production_clause = ""
    if production is not None and yield_per_ha is not None:
        production_clause = (
            f"For a land area of {area:,.0f} hectares during the {season} season, "
            f"the estimated production is approximately {_format_tonnes(production)} "
            f"with an expected yield of {yield_per_ha:,.2f} tonnes per hectare."
        )
    else:
        production_clause = (
            f"For a land area of {area:,.0f} hectares during the {season} season, "
            f"a production estimate could not be generated for this location-crop combination."
        )

    fertilizer_clause = ""
    if fertilizer and "primary_fertilizer" in fertilizer:
        fertilizer_clause = (
            f" {fertilizer['primary_fertilizer']} fertilizer is recommended "
            f"({fertilizer['application_timing'].split('.')[0].lower()}), "
            f"with {fertilizer['alternative_fertilizer']} as an alternative."
        )

    return (
        f"Based on the {weather_clause}, historical crop patterns and environmental conditions, "
        f"**{crop}** is the most suitable crop for cultivation "
        f"(model confidence: {confidence:.0f}%). "
        f"{production_clause}"
        f"{fertilizer_clause}"
    ).replace("  ", " ").strip()
