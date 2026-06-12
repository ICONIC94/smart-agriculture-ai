"""Intelligent farming assistant – Crop Recommendation page."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from utils.farm_assistant import analyze_farm
from utils.location import format_location_pins, get_coordinates
from utils.loaders import (
    get_districts_for_state,
    load_crop_artifacts,
    load_fertilizer_dataset,
    load_production_artifacts,
    load_production_dataset,
)
from utils.season import detect_season


def _on_farm_state_change() -> None:
    st.session_state.farm_district = ""


def _render_step_header(icon: str, title: str) -> None:
    """Render workflow step header."""
    st.markdown(
        f"""
        <div class="workflow-step-header">
            <span class="step-icon">{icon}</span>
            <h3 class="step-title">{title}</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_weather_card(weather: dict) -> None:
    """Render weather metrics as a styled grid."""
    rainfall_show = weather.get("rainfall_display", weather["rainfall"])
    st.markdown(
        f"""
        <div class="weather-card">
            <div class="weather-stat"><div class="label">Temperature</div><div class="value">{weather['temperature']}°C</div></div>
            <div class="weather-stat"><div class="label">Humidity</div><div class="value">{weather['humidity']}%</div></div>
            <div class="weather-stat"><div class="label">Rainfall</div><div class="value">{rainfall_show} mm</div></div>
            <div class="weather-stat"><div class="label">Condition</div><div class="value">{weather.get('condition', 'N/A')}</div></div>
            <div class="weather-stat"><div class="label">Wind</div><div class="value">{weather.get('wind_speed', 0)} km/h</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_crop_recommendation(crop: dict) -> None:
    """Render recommended crop and top alternatives using native Streamlit layout."""
    st.markdown(
        f"""
        <div class="crop-result-card">
            <div class="result-label">🌱 Recommended Crop</div>
            <p class="crop-name">{crop['display_name']}</p>
            <p class="confidence">Model confidence: {crop['confidence_pct']:.0f}%</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    alternatives = crop.get("alternatives", [])
    if not alternatives:
        st.caption("No alternatives available.")
        return

    st.markdown("**Top Alternatives**")
    medals = ["🥇", "🥈", "🥉"]
    for medal, alt in zip(medals, alternatives[:3]):
        with st.container():
            col_name, col_conf = st.columns([2, 1])
            with col_name:
                st.markdown(f"### {medal} {alt['crop']}")
            with col_conf:
                st.markdown(f"**Confidence:** {alt['confidence_pct']:.0f}%")


def _render_harvest_card(production: dict) -> None:
    """Render production estimate card."""
    if not production.get("available"):
        st.caption("Production estimate unavailable for this location and crop combination.")
        return

    tonnes = production["production_tonnes"]
    if tonnes >= 1000:
        display_prod = f"{tonnes:,.1f} tonnes"
    elif tonnes >= 1:
        display_prod = f"{tonnes:,.2f} tonnes"
    else:
        display_prod = f"{tonnes * 1000:,.0f} kg"

    st.markdown(
        f"""
        <div class="harvest-card">
            <div class="harvest-title">🌾 Estimated Harvest</div>
            <p class="harvest-value">{display_prod}</p>
            <div class="harvest-grid">
                <div class="harvest-stat">
                    <div class="label">Expected Production</div>
                    <div class="value">{tonnes:,.1f} tonnes</div>
                </div>
                <div class="harvest-stat">
                    <div class="label">Yield per hectare</div>
                    <div class="value">{production['yield_per_hectare']:,.2f} t/ha</div>
                </div>
                <div class="harvest-stat">
                    <div class="label">Farm Area</div>
                    <div class="value">{production['area_hectares']:,.0f} ha</div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_fertilizer_cards(fertilizer: dict) -> None:
    """Render fertilizer recommendation cards."""
    if not fertilizer or "primary_fertilizer" not in fertilizer:
        st.caption("Fertilizer recommendation unavailable for this crop.")
        return

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f"""
            <div class="fert-card primary">
                <h4>🧪 Best Fertilizer</h4>
                <p style="font-size:1.2rem;font-weight:700;color:#145C37;">{fertilizer['primary_fertilizer']}</p>
                <p>{fertilizer['application_timing']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"""
            <div class="fert-card">
                <h4>Alternative</h4>
                <p style="font-size:1.1rem;font-weight:700;color:#1A2E22;">{fertilizer['alternative_fertilizer']}</p>
                <p>{fertilizer['guidance']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_location_step(report: dict) -> None:
    """Render interactive location preview with map."""
    loc = report["location"]
    lat, lon = get_coordinates(loc["state"], loc["district"])
    map_df = pd.DataFrame({"lat": [lat], "lon": [lon]})

    pin_col, map_col = st.columns([1, 2])
    with pin_col:
        st.markdown(
            f"""
            <div class="location-pins">
                <p>{format_location_pins(loc['state'], loc['district']).replace(chr(10), '<br>')}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with map_col:
        st.map(map_df, use_container_width=True)

    info_col1, info_col2, info_col3, info_col4 = st.columns(4)
    with info_col1:
        st.metric("State", loc["state"])
    with info_col2:
        st.metric("District", loc["district"])
    with info_col3:
        st.metric("Land Area", f"{report['production']['area_hectares']:,.0f} ha")
    with info_col4:
        st.metric("Soil pH", f"{report['soil_ph']:.1f}")


def _render_workflow_results(report: dict) -> None:
    """Render the full vertical workflow output."""
    with st.container():
        _render_step_header("📍", "Step 1 — Location")
        _render_location_step(report)
        st.markdown('<div class="workflow-connector">↓</div>', unsafe_allow_html=True)

    with st.container():
        _render_step_header("🌤", "Step 2 — Live Weather")
        _render_weather_card(report["weather"])
        weather_note = (
            " (manual entry)"
            if report.get("weather_manual")
            else f" via {report['weather'].get('source', 'API')}"
        )
        st.caption(f"Source{weather_note}")
        st.markdown('<div class="workflow-connector">↓</div>', unsafe_allow_html=True)

    with st.container():
        _render_step_header("🌱", "Step 3 — Crop Recommendation")
        _render_crop_recommendation(report["crop"])
        st.markdown('<div class="workflow-connector">↓</div>', unsafe_allow_html=True)

    with st.container():
        _render_step_header("🌾", "Step 4 — Production Estimation")
        _render_harvest_card(report["production"])
        st.markdown('<div class="workflow-connector">↓</div>', unsafe_allow_html=True)

    with st.container():
        _render_step_header("🧪", "Step 5 — Fertilizer Recommendation")
        _render_fertilizer_cards(report.get("fertilizer", {}))
        st.markdown('<div class="workflow-connector">↓</div>', unsafe_allow_html=True)

    with st.container():
        _render_step_header("📝", "Step 6 — AI Summary")
        explanation = report.get("explanation", "").replace("**", "")
        st.markdown(
            f'<div class="explanation-card">{explanation}</div>',
            unsafe_allow_html=True,
        )


def render_crop_recommendation() -> None:
    """Render the intelligent farming assistant page."""
    season_info = detect_season()

    try:
        production_df = load_production_dataset()
    except Exception:
        st.warning("⚠ Unable to load location data. Please try again later.")
        return

    states = sorted(production_df["State_Name"].dropna().unique().tolist())

    st.markdown(
        """
        <div class="farm-page">
            <div class="page-header">
                <h1>🌱 Crop Recommendation</h1>
                <p>Enter your farm location and get a complete AI-powered cultivation plan in one click.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="season-badge">📅 Detected Season: <strong>{season_info["season"]}</strong> — {season_info["description"]}</div>',
        unsafe_allow_html=True,
    )

    if "farm_report" not in st.session_state:
        st.session_state.farm_report = None
    if "needs_manual_weather" not in st.session_state:
        st.session_state.needs_manual_weather = False
    if "farm_state" not in st.session_state:
        st.session_state.farm_state = ""
    if "farm_district" not in st.session_state:
        st.session_state.farm_district = ""

    col1, col2 = st.columns(2)
    with col1:
        st.selectbox(
            "State",
            options=[""] + states,
            format_func=lambda x: x or "Select your state",
            key="farm_state",
            on_change=_on_farm_state_change,
        )
        districts = (
            get_districts_for_state(production_df, st.session_state.farm_state)
            if st.session_state.farm_state
            else []
        )
        if st.session_state.farm_district not in districts:
            st.session_state.farm_district = ""
        st.selectbox(
            "District",
            options=[""] + districts,
            format_func=lambda x: x or "Select your district",
            disabled=not st.session_state.farm_state,
            key="farm_district",
        )
    with col2:
        area = st.number_input(
            "Land Area (hectares)",
            min_value=0.1,
            value=100.0,
            step=1.0,
            format="%.1f",
        )
        ph_input = st.text_input(
            "Optional Soil pH (leave blank for 6.5)",
            placeholder="e.g. 6.5",
        )

    show_manual = st.session_state.needs_manual_weather
    manual_weather = None
    if show_manual:
        st.warning("⚠ Unable to fetch weather. Enter values manually to continue.")
        mc1, mc2, mc3 = st.columns(3)
        with mc1:
            manual_temp = st.number_input("Temperature (°C)", value=28.0, step=0.5)
        with mc2:
            manual_humidity = st.number_input(
                "Humidity (%)", value=75.0, step=1.0, min_value=0.0, max_value=100.0
            )
        with mc3:
            manual_rainfall = st.number_input("Rainfall (mm)", value=200.0, step=1.0, min_value=0.0)
        manual_weather = {
            "temperature": manual_temp,
            "humidity": manual_humidity,
            "rainfall": manual_rainfall,
        }

    analyze_clicked = st.button("🚀 Analyze My Farm", use_container_width=True, type="primary")

    if analyze_clicked:
        state = st.session_state.farm_state
        district = st.session_state.farm_district
        soil_ph = 6.5

        if not state or not district:
            st.warning("⚠ Please select all required inputs.")
        elif ph_input.strip():
            try:
                soil_ph = float(ph_input.strip())
                if soil_ph < 0 or soil_ph > 14:
                    st.warning("⚠ Soil pH must be between 0 and 14.")
                    soil_ph = None
            except ValueError:
                st.warning("⚠ Invalid soil pH value. Leave blank to use 6.5.")
                soil_ph = None

        if soil_ph is not None and state and district:
            try:
                crop_artifact, label_encoder = load_crop_artifacts()
                prod_model, prod_preprocessor = load_production_artifacts()
                fertilizer_df = load_fertilizer_dataset()
            except Exception:
                st.warning("⚠ Prediction unavailable. Models could not be loaded.")
                return

            with st.spinner("Analyzing your farm — fetching weather, running AI models..."):
                try:
                    report = analyze_farm(
                        state=state,
                        district=district,
                        area=area,
                        soil_ph=soil_ph,
                        crop_artifact=crop_artifact,
                        label_encoder=label_encoder,
                        production_model=prod_model,
                        production_preprocessor=prod_preprocessor,
                        production_df=production_df,
                        fertilizer_df=fertilizer_df,
                        manual_weather=manual_weather,
                    )
                except Exception:
                    st.warning("⚠ Prediction unavailable. Please try again.")
                    return

            if report.get("needs_manual_weather"):
                st.session_state.needs_manual_weather = True
                st.warning(report.get("error", "⚠ Unable to fetch weather."))
                return

            if "error" in report:
                st.warning(report["error"])
                return

            st.session_state.needs_manual_weather = False
            st.session_state.farm_report = report

            for warning in report.get("warnings", []):
                st.warning(warning)

    if st.session_state.farm_report:
        _render_workflow_results(st.session_state.farm_report)
