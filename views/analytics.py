"""Analytics dashboard page."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.loaders import load_crop_dataset, load_production_dataset

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans, sans-serif", color="#1A2E22"),
    margin=dict(l=20, r=20, t=50, b=20),
    colorway=["#1B7F4B", "#2ECC71", "#145C37", "#52BE80", "#27AE60", "#1E8449"],
)


def _apply_layout(fig: go.Figure, title: str) -> go.Figure:
    """Apply consistent Plotly layout styling."""
    fig.update_layout(title=dict(text=title, x=0, xanchor="left"), **PLOTLY_LAYOUT)
    return fig


def render_analytics() -> None:
    """Render interactive analytics charts."""
    st.markdown(
        """
        <div class="page-header">
            <h1>Analytics Dashboard</h1>
            <p>Explore crop distribution and production trends across India.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    crop_df = load_crop_dataset()
    production_df = load_production_dataset()

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        [
            "Crop Distribution",
            "State Production",
            "Season Production",
            "Top Crops",
            "Year Trends",
        ]
    )

    with tab1:
        crop_counts = crop_df["label"].value_counts().reset_index()
        crop_counts.columns = ["Crop", "Count"]
        fig = px.pie(
            crop_counts,
            names="Crop",
            values="Count",
            hole=0.45,
            title="",
        )
        fig.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(_apply_layout(fig, "Crop Distribution (Recommendation Dataset)"), use_container_width=True)

    with tab2:
        state_prod = (
            production_df.groupby("State_Name", as_index=False)["Production"]
            .sum()
            .sort_values("Production", ascending=False)
            .head(20)
        )
        fig = px.bar(
            state_prod,
            x="Production",
            y="State_Name",
            orientation="h",
            labels={"State_Name": "State", "Production": "Total Production"},
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(_apply_layout(fig, "Top 20 States by Total Production"), use_container_width=True)

    with tab3:
        season_df = production_df.copy()
        season_df["Season"] = season_df["Season"].str.strip()
        season_prod = (
            season_df.groupby("Season", as_index=False)["Production"]
            .sum()
            .sort_values("Production", ascending=False)
        )
        fig = px.bar(
            season_prod,
            x="Season",
            y="Production",
            labels={"Season": "Season", "Production": "Total Production"},
        )
        st.plotly_chart(_apply_layout(fig, "Season-wise Total Production"), use_container_width=True)

    with tab4:
        top_crops = (
            production_df.groupby("Crop", as_index=False)["Production"]
            .sum()
            .sort_values("Production", ascending=False)
            .head(15)
        )
        fig = px.treemap(
            top_crops,
            path=["Crop"],
            values="Production",
            color="Production",
            color_continuous_scale=["#E8F5EE", "#1B7F4B"],
        )
        st.plotly_chart(_apply_layout(fig, "Top 15 Crops by Production"), use_container_width=True)

    with tab5:
        year_prod = (
            production_df.groupby("Crop_Year", as_index=False)["Production"]
            .sum()
            .sort_values("Crop_Year")
        )
        fig = px.line(
            year_prod,
            x="Crop_Year",
            y="Production",
            markers=True,
            labels={"Crop_Year": "Year", "Production": "Total Production"},
        )
        fig.update_traces(line=dict(color="#1B7F4B", width=3))
        st.plotly_chart(_apply_layout(fig, "Year-wise Total Production Trend"), use_container_width=True)

    st.caption(
        "Charts are rendered with Plotly using MergeFileCrop.csv and "
        "raw_districtwise_yield_data.csv. Large production values may reflect "
        "aggregate units as recorded in the source dataset."
    )
