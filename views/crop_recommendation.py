"""Crop recommendation page."""

from __future__ import annotations

import streamlit as st

from utils.inference import predict_crop
from utils.loaders import get_crop_feature_ranges, load_crop_artifacts, load_crop_dataset


def render_crop_recommendation() -> None:
    """Render the crop recommendation form and prediction result."""
    st.markdown(
        """
        <div class="page-header">
            <h1>Crop Recommendation</h1>
            <p>Enter environmental conditions to get an AI-powered crop suggestion.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    crop_df = load_crop_dataset()
    ranges = get_crop_feature_ranges(crop_df)
    artifact, label_encoder = load_crop_artifacts()

    with st.form("crop_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        with col1:
            temperature = st.slider(
                "Temperature (°C)",
                min_value=float(ranges["temperature"][0]),
                max_value=float(ranges["temperature"][1]),
                value=25.0,
                step=0.1,
            )
            humidity = st.slider(
                "Humidity (%)",
                min_value=0.0,
                max_value=100.0,
                value=80.0,
                step=0.5,
            )
        with col2:
            ph = st.slider(
                "pH",
                min_value=0.0,
                max_value=14.0,
                value=6.5,
                step=0.1,
            )
            rainfall = st.slider(
                "Rainfall (mm)",
                min_value=0.0,
                max_value=float(ranges["rainfall"][1]),
                value=200.0,
                step=1.0,
            )

        submitted = st.form_submit_button("Recommend Crop", use_container_width=True)

    if submitted:
        result = predict_crop(artifact, label_encoder, temperature, humidity, ph, rainfall)
        if "error" in result:
            st.error(result["error"])
            return

        confidence_pct = result["confidence"] * 100
        st.markdown(
            f"""
            <div class="result-card">
                <div class="result-label">Recommended Crop</div>
                <p class="result-value">{result['crop']}</p>
                <div class="result-meta">Model confidence: {confidence_pct:.1f}%</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("#### Top Alternatives")
        alt_cols = st.columns(len(result["alternatives"]))
        for column, alt in zip(alt_cols, result["alternatives"]):
            with column:
                st.markdown(
                    f"""
                    <div class="info-card">
                        <h3>{alt['crop'].title()}</h3>
                        <p class="metric-value">{alt['confidence'] * 100:.1f}%</p>
                        <p>Confidence score</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    with st.expander("Input Guidelines"):
        st.markdown(
            """
            - **Temperature**: Typical range observed in the training dataset.
            - **Humidity**: Relative humidity between 0–100%.
            - **pH**: Soil acidity/alkalinity on a 0–14 scale.
            - **Rainfall**: Annual or seasonal rainfall in millimeters.
            """
        )
