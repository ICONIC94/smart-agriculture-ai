"""Live weather fetching via WeatherAPI.com or OpenWeatherMap."""

from __future__ import annotations

import os
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()

WEATHER_TIMEOUT = 8


def _get_api_config() -> tuple[str, str]:
    """Load weather provider and API key from environment."""
    provider = os.getenv("WEATHER_API_PROVIDER", "weatherapi").strip().lower()
    api_key = os.getenv("WEATHER_API_KEY", "").strip()
    return provider, api_key


def _estimate_model_rainfall(current_precip: float, forecast_total: float, days: int) -> float:
    """
    Convert short-term precipitation into a rainfall estimate for the crop model.

    The crop model was trained on values roughly between 20–300 mm.
    """
    if days <= 0:
        monthly_estimate = current_precip * 30
    else:
        monthly_estimate = forecast_total * (30 / days)

    rainfall = max(monthly_estimate, current_precip * 10, 80.0)
    return round(min(rainfall, 298.0), 1)


def _fetch_weatherapi(state: str, district: str, api_key: str) -> dict[str, Any]:
    """Fetch weather from WeatherAPI.com."""
    query = f"{district}, {state}, India"
    current_url = "https://api.weatherapi.com/v1/current.json"
    forecast_url = "https://api.weatherapi.com/v1/forecast.json"

    current_resp = requests.get(
        current_url,
        params={"key": api_key, "q": query, "aqi": "no"},
        timeout=WEATHER_TIMEOUT,
    )
    current_resp.raise_for_status()
    current_data = current_resp.json()

    forecast_resp = requests.get(
        forecast_url,
        params={"key": api_key, "q": query, "days": 3, "aqi": "no"},
        timeout=WEATHER_TIMEOUT,
    )
    forecast_resp.raise_for_status()
    forecast_data = forecast_resp.json()

    current = current_data["current"]
    forecast_days = forecast_data.get("forecast", {}).get("forecastday", [])
    forecast_total = sum(day["day"]["totalprecip_mm"] for day in forecast_days)
    current_precip = float(current.get("precip_mm", 0.0))

    return {
        "temperature": round(float(current["temp_c"]), 1),
        "humidity": round(float(current["humidity"]), 1),
        "rainfall": _estimate_model_rainfall(current_precip, forecast_total, len(forecast_days)),
        "rainfall_display": round(max(current_precip, forecast_total / max(len(forecast_days), 1)), 1),
        "condition": current["condition"]["text"],
        "wind_speed": round(float(current["wind_kph"]), 1),
        "source": "WeatherAPI.com",
        "location": query,
    }


def _fetch_openweathermap(state: str, district: str, api_key: str) -> dict[str, Any]:
    """Fetch weather from OpenWeatherMap using geocoding + current weather."""
    geo_url = "https://api.openweathermap.org/geo/1.0/direct"
    geo_resp = requests.get(
        geo_url,
        params={"q": f"{district}, {state}, IN", "limit": 1, "appid": api_key},
        timeout=WEATHER_TIMEOUT,
    )
    geo_resp.raise_for_status()
    geo_data = geo_resp.json()
    if not geo_data:
        raise ValueError(f"Location not found: {district}, {state}")

    lat = geo_data[0]["lat"]
    lon = geo_data[0]["lon"]

    weather_url = "https://api.openweathermap.org/data/2.5/weather"
    weather_resp = requests.get(
        weather_url,
        params={"lat": lat, "lon": lon, "appid": api_key, "units": "metric"},
        timeout=WEATHER_TIMEOUT,
    )
    weather_resp.raise_for_status()
    data = weather_resp.json()

    rain = data.get("rain", {})
    current_precip = float(rain.get("1h", rain.get("3h", 0.0)))

    return {
        "temperature": round(float(data["main"]["temp"]), 1),
        "humidity": round(float(data["main"]["humidity"]), 1),
        "rainfall": _estimate_model_rainfall(current_precip, current_precip * 3, 3),
        "rainfall_display": round(current_precip, 1),
        "condition": data["weather"][0]["description"].title(),
        "wind_speed": round(float(data["wind"]["speed"]) * 3.6, 1),
        "source": "OpenWeatherMap",
        "location": f"{district}, {state}, India",
    }


def fetch_live_weather(state: str, district: str) -> dict[str, Any]:
    """
    Fetch live weather for a state/district pair.

    Returns a dict with weather fields on success, or {"error": ...} on failure.
    """
    if not state or not district:
        return {"error": "State and district are required for weather lookup."}

    provider, api_key = _get_api_config()
    if not api_key:
        return {"error": "⚠ Unable to fetch weather. Weather API key is not configured."}

    try:
        if provider == "openweathermap":
            weather = _fetch_openweathermap(state, district, api_key)
        else:
            weather = _fetch_weatherapi(state, district, api_key)
        weather["success"] = True
        return weather
    except requests.Timeout:
        return {"error": "⚠ Unable to fetch weather. Please try again or enter values manually."}
    except requests.HTTPError:
        return {"error": "⚠ Unable to fetch weather. Check your API key and location."}
    except (requests.RequestException, ValueError, KeyError):
        return {"error": "⚠ Unable to fetch weather."}
