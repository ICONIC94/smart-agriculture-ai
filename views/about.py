"""About page."""

from __future__ import annotations

import streamlit as st

from utils.loaders import load_crop_metrics, load_production_metrics


def render_about() -> None:
    """Render project information, datasets, and model details."""
    st.markdown(
        """
        <div class="page-header">
            <h1>About AgriSense AI</h1>
            <p>Learn about the datasets, technologies, and models powering this platform.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    crop_metrics = load_crop_metrics()
    production_metrics = load_production_metrics()

    st.markdown("### Mission")
    st.markdown(
        """
        AgriSense AI helps farmers, agronomists, and policymakers make informed decisions
        by combining machine learning predictions with interactive analytics. The platform
        loads pre-trained models at startup and never retrains during inference.
        """
    )

    st.markdown("### Datasets")
    datasets = [
        (
            "MergeFileCrop.csv",
            "Crop recommendation dataset with temperature, humidity, pH, rainfall, and crop labels.",
        ),
        (
            "raw_districtwise_yield_data.csv",
            "District-wise agricultural production records across Indian states.",
        ),
        (
            "Fertilizer.csv",
            "Crop-specific NPK and pH fertilizer recommendations for lookup-based guidance.",
        ),
    ]
    for name, description in datasets:
        st.markdown(
            f"""
            <div class="info-card" style="margin-bottom: 0.75rem;">
                <h3>{name}</h3>
                <p>{description}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("### Models")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f"""
            <div class="info-card">
                <h3>Crop Recommendation</h3>
                <p><strong>Best Model:</strong> {crop_metrics['best_model']}</p>
                <p><strong>Classes:</strong> {crop_metrics['n_classes']}</p>
                <p><strong>Test F1 (macro):</strong> {crop_metrics['models'][crop_metrics['best_model']]['f1_macro']:.4f}</p>
                <p><strong>Features:</strong> temperature, humidity, pH, rainfall</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with col2:
        best = production_metrics["best_model"]
        st.markdown(
            f"""
            <div class="info-card">
                <h3>Production Prediction</h3>
                <p><strong>Best Model:</strong> {best}</p>
                <p><strong>R² Score:</strong> {production_metrics['models'][best]['r2']:.4f}</p>
                <p><strong>RMSE:</strong> {production_metrics['models'][best]['rmse']:,.2f}</p>
                <p><strong>Features:</strong> state, district, year, season, crop, area</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("### Technology Stack")
    tech_items = [
        "**Streamlit** — Interactive web application framework",
        "**Plotly** — Interactive analytics visualizations",
        "**scikit-learn** — Preprocessing pipelines and evaluation",
        "**XGBoost & CatBoost** — Gradient boosting models",
        "**pandas & NumPy** — Data manipulation",
        "**joblib** — Model serialization and loading",
    ]
    for item in tech_items:
        st.markdown(f"- {item}")

    st.markdown("### Training Scripts")
    st.code(
        "python src/train_crop.py\npython src/train_production.py",
        language="bash",
    )
    st.caption("Training is performed offline. The Streamlit app only loads saved artifacts.")
