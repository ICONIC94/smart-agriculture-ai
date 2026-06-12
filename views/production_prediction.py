"""Production prediction page."""

from __future__ import annotations

import streamlit as st

from utils.inference import predict_production
from utils.loaders import (
    get_districts_for_state,
    get_filtered_production_options,
    get_reference_crop_year,
    load_production_artifacts,
    load_production_dataset,
)


def _format_estimated_production(tonnes: float) -> str:
    """Format production values (dataset units are tonnes)."""
    if tonnes < 1:
        return f"{tonnes * 1000:,.0f} kg"
    if tonnes >= 1000:
        return f"{tonnes:,.1f} tonnes"
    return f"{tonnes:,.2f} tonnes"


def _on_prod_state_change() -> None:
    st.session_state.prod_district = ""
    st.session_state.prod_season = ""
    st.session_state.prod_crop = ""


def _on_prod_district_change() -> None:
    st.session_state.prod_season = ""
    st.session_state.prod_crop = ""


def render_production_prediction() -> None:
    """Render the production estimation form and result card."""
    st.markdown(
        """
        <div class="page-header">
            <h1>Production Estimation</h1>
            <p>Estimate expected crop production using historical patterns learned by the AI model.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        df = load_production_dataset()
        model, preprocessor = load_production_artifacts()
    except Exception:
        st.warning("⚠ Prediction unavailable. Model artifacts could not be loaded.")
        return

    if "prod_state" not in st.session_state:
        st.session_state.prod_state = ""
    if "prod_district" not in st.session_state:
        st.session_state.prod_district = ""
    if "prod_season" not in st.session_state:
        st.session_state.prod_season = ""
    if "prod_crop" not in st.session_state:
        st.session_state.prod_crop = ""

    states = sorted(df["State_Name"].dropna().unique().tolist())

    col1, col2 = st.columns(2)
    with col1:
        st.selectbox(
            "State",
            options=[""] + states,
            format_func=lambda x: x or "Select state",
            key="prod_state",
            on_change=_on_prod_state_change,
        )
        districts = (
            get_districts_for_state(df, st.session_state.prod_state)
            if st.session_state.prod_state
            else []
        )
        if st.session_state.prod_district not in districts:
            st.session_state.prod_district = ""
        st.selectbox(
            "District",
            options=[""] + districts,
            format_func=lambda x: x or "Select district",
            disabled=not st.session_state.prod_state,
            key="prod_district",
            on_change=_on_prod_district_change,
        )

    filtered = get_filtered_production_options(
        df,
        st.session_state.prod_state or None,
        st.session_state.prod_district or None,
    )
    seasons = filtered["seasons"] if filtered["seasons"] else sorted(df["Season"].dropna().unique().tolist())
    crops = filtered["crops"] if filtered["crops"] else sorted(df["Crop"].dropna().unique().tolist())

    if st.session_state.prod_season not in seasons:
        st.session_state.prod_season = ""
    if st.session_state.prod_crop not in crops:
        st.session_state.prod_crop = ""

    with col2:
        st.selectbox(
            "Season",
            options=[""] + seasons,
            format_func=lambda x: x.strip() if x else "Select season",
            disabled=not st.session_state.prod_state,
            key="prod_season",
        )
        st.selectbox(
            "Crop",
            options=[""] + crops,
            format_func=lambda x: x or "Select crop",
            disabled=not st.session_state.prod_state,
            key="prod_crop",
        )
        area = st.number_input(
            "Area (hectares)",
            min_value=0.0,
            value=100.0,
            step=10.0,
            format="%.2f",
        )

    state = st.session_state.prod_state
    district = st.session_state.prod_district
    season = st.session_state.prod_season
    crop = st.session_state.prod_crop

    if st.button("Estimate Production", use_container_width=True):
        try:
            reference_year = get_reference_crop_year(df, state, district, season, crop)
            result = predict_production(
                model,
                preprocessor,
                state,
                district,
                reference_year,
                season,
                crop,
                area,
            )
        except Exception:
            st.warning("⚠ Prediction unavailable.")
            return

        if "error" in result:
            st.warning(result["error"])
            return

        production = result["production"]
        yield_per_ha = production / area if area > 0 else 0.0

        st.markdown(
            f"""
            <div class="result-card">
                <div class="result-label">Estimated Total Production</div>
                <p class="result-value">{_format_estimated_production(production)}</p>
                <div class="result-meta">
                    Based on learned historical patterns · not a selected crop year
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        metric_col1, metric_col2, metric_col3 = st.columns(3)
        with metric_col1:
            st.metric("Estimated Yield per hectare", f"{yield_per_ha:,.2f} t/ha")
        with metric_col2:
            st.metric("Area", f"{area:,.2f} ha")
        with metric_col3:
            st.metric("Crop", crop)

        detail_col1, detail_col2 = st.columns(2)
        with detail_col1:
            st.metric("District", district)
        with detail_col2:
            st.metric("Season", season.strip())

        st.caption(
            "Larger land area generally results in higher production assuming similar growing conditions."
        )
        st.info(
            "This estimate is generated using historical production trends learned by the AI model "
            "and should be treated as an expected estimate rather than an exact future value."
        )

    with st.expander("About this model"):
        st.markdown(
            """
            Estimates are generated by a pre-trained **XGBoost** regressor (R² ≈ 0.96)
            using state, district, season, crop type, and cultivated area. The model internally
            references the most recent historical year available for your selection — you do not
            need to choose a crop year manually.
            """
        )
