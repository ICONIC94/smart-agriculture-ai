"""Automatic agricultural season detection."""

from __future__ import annotations

from datetime import date


def detect_season(reference: date | None = None) -> dict[str, str]:
    """
    Detect the current Indian agricultural season from the calendar month.

    Returns a dict with display name and the value used by the production model.
    """
    today = reference or date.today()
    month = today.month

    if month in (6, 7, 8, 9, 10):
        season = "Kharif"
        description = "Monsoon sowing season (June–October)"
    elif month in (11, 12, 1, 2, 3):
        season = "Rabi"
        description = "Winter cropping season (November–March)"
    elif month == 4:
        season = "Summer"
        description = "Summer cropping season (April)"
    elif month == 5:
        season = "Kharif"
        description = "Pre-monsoon / early Kharif preparation (May)"
    else:
        season = "Whole Year"
        description = "Year-round cultivation"

    return {
        "season": season,
        "description": description,
        "month": today.strftime("%B"),
        "year": str(today.year),
    }
