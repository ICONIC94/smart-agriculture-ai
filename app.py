"""
AgriSense AI – Smart Agriculture Platform

Run with: streamlit run app.py
"""

from __future__ import annotations

import streamlit as st

from views.about import render_about
from views.crop_recommendation import render_crop_recommendation
from views.fertilizer import render_fertilizer_recommendation
from views.home import render_home
from views.production_prediction import render_production_prediction
from utils.config import APP_SUBTITLE, APP_TITLE, NAV_ITEMS
from utils.styles import THEME_CSS

st.set_page_config(
    page_title=f"{APP_TITLE} – {APP_SUBTITLE}",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(THEME_CSS, unsafe_allow_html=True)

PAGE_RENDERERS = {
    "home": render_home,
    "crop": render_crop_recommendation,
    "production": render_production_prediction,
    "fertilizer": render_fertilizer_recommendation,
    "about": render_about,
}

NAV_LABELS = {key: label for key, label, _icon in NAV_ITEMS}
NAV_OPTIONS = list(NAV_LABELS.keys())


def render_sidebar() -> str:
    """Render branded sidebar navigation and return selected page key."""
    with st.sidebar:
        st.markdown(
            f"""
            <div class="sidebar-brand">
                <h2>🌾 {APP_TITLE}</h2>
                <p>{APP_SUBTITLE}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        selection = st.radio(
            "Navigation",
            options=NAV_OPTIONS,
            format_func=lambda key: NAV_LABELS[key],
            label_visibility="collapsed",
        )

        st.markdown("---")
        st.caption("Pre-trained ML models · No retraining at runtime")
        st.caption("Built with Streamlit")

    return selection


def main() -> None:
    """Application entry point."""
    selected_page = render_sidebar()
    renderer = PAGE_RENDERERS.get(selected_page, render_home)
    renderer()


if __name__ == "__main__":
    main()
