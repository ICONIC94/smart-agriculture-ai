"""Fertilizer recommendation page."""

from __future__ import annotations

import streamlit as st

from utils.inference import lookup_fertilizer
from utils.loaders import load_fertilizer_dataset


def render_fertilizer_recommendation() -> None:
    """Render fertilizer lookup form and recommendation card."""
    st.markdown(
        """
        <div class="page-header">
            <h1>Fertilizer Recommendation</h1>
            <p>Lookup NPK and pH guidance for your crop from the fertilizer dataset.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    fertilizer_df = load_fertilizer_dataset()
    crops = sorted(fertilizer_df["Crop"].dropna().unique().tolist())

    col1, col2 = st.columns([2, 1])
    with col1:
        selected_crop = st.selectbox(
            "Select Crop",
            options=[""] + crops,
            format_func=lambda x: x or "Choose a crop",
        )
    with col2:
        search_term = st.text_input("Or search crop", placeholder="e.g. Rice, Maize")

    crop_query = search_term.strip() or selected_crop

    if st.button("Get Recommendation", use_container_width=True):
        result = lookup_fertilizer(fertilizer_df, crop_query)
        if "error" in result:
            st.warning(result["error"])
            return

        st.markdown(
            f"""
            <div class="result-card">
                <div class="result-label">Fertilizer Plan for</div>
                <p class="result-value">{result['crop']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="fertilizer-grid">
                <div class="fertilizer-item"><span>Nitrogen (N)</span><strong>{result['N']:.0f}</strong></div>
                <div class="fertilizer-item"><span>Phosphorus (P)</span><strong>{result['P']:.0f}</strong></div>
                <div class="fertilizer-item"><span>Potassium (K)</span><strong>{result['K']:.0f}</strong></div>
                <div class="fertilizer-item"><span>Ideal pH</span><strong>{result['pH']:.1f}</strong></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.success(
            f"Apply balanced fertilization for **{result['crop']}** with "
            f"N={result['N']:.0f}, P={result['P']:.0f}, K={result['K']:.0f} "
            f"at soil pH ≈ {result['pH']:.1f}."
        )

    with st.expander("How it works"):
        st.markdown(
            """
            This module uses **Fertilizer.csv** as a rule-based lookup table.
            Select a crop from the dropdown or search by name to retrieve recommended
            nitrogen, phosphorus, potassium, and ideal soil pH values.
            """
        )
