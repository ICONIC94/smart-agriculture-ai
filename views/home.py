"""Home page for AgriSense AI."""

from __future__ import annotations

import streamlit as st

from utils.loaders import load_crop_dataset, load_production_dataset


def render_home() -> None:
    """Render the landing page with hero section and overview cards."""
    st.markdown(
        """
        <div class="hero-section">
            <div class="hero-badge">AI-Powered Agriculture Intelligence</div>
            <h1 class="hero-title">AgriSense AI – Smart Agriculture Platform</h1>
            <p class="hero-subtitle">
                Make data-driven farming decisions with machine learning crop recommendations,
                production forecasting, fertilizer guidance, and interactive analytics — all in
                one modern dashboard.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    crop_df = load_crop_dataset()
    production_df = load_production_dataset()

    col1, col2, col3, col4 = st.columns(4)
    metrics = [
        (col1, "Crop Classes", f"{crop_df['label'].nunique()}", "Supported recommendation targets"),
        (col2, "Crop Records", f"{len(crop_df):,}", "Environmental training samples"),
        (col3, "Production Records", f"{len(production_df):,}", "District-wise yield entries"),
        (col4, "States Covered", f"{production_df['State_Name'].nunique()}", "Pan-India coverage"),
    ]
    for column, title, value, subtitle in metrics:
        with column:
            st.markdown(
                f"""
                <div class="metric-card">
                    <h3>{title}</h3>
                    <p class="metric-value">{value}</p>
                    <p>{subtitle}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Platform Capabilities")

    features = [
        (
            "Crop Recommendation",
            "Predict the best crop for your soil and climate using a trained CatBoost classifier.",
        ),
        (
            "Production Forecasting",
            "Estimate district-level crop production with an XGBoost regression model.",
        ),
        (
            "Fertilizer Guidance",
            "Get NPK and pH recommendations from a curated fertilizer lookup dataset.",
        ),
        (
            "Analytics Dashboard",
            "Explore crop distribution, seasonal trends, and production insights with Plotly.",
        ),
    ]

    row1_col1, row1_col2 = st.columns(2)
    row2_col1, row2_col2 = st.columns(2)
    for column, (title, description) in zip(
        [row1_col1, row1_col2, row2_col1, row2_col2], features
    ):
        with column:
            st.markdown(
                f"""
                <div class="feature-card">
                    <h3>{title}</h3>
                    <p>{description}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.info(
        "Use the sidebar to navigate between modules. All predictions use pre-trained "
        "models — no retraining occurs at runtime."
    )
