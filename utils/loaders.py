"""Cached data and model loaders for the Streamlit application."""

from __future__ import annotations

import json
from typing import Any

import joblib
import pandas as pd
import streamlit as st

from utils.config import (
    CROP_DATA_PATH,
    CROP_FEATURE_COLUMNS,
    CROP_LABEL_ENCODER_PATH,
    CROP_METRICS_PATH,
    CROP_MODEL_PATH,
    FERTILIZER_DATA_PATH,
    PRODUCTION_DATA_PATH,
    PRODUCTION_METRICS_PATH,
    PRODUCTION_MODEL_PATH,
    PRODUCTION_PREPROCESSOR_PATH,
)


@st.cache_data(show_spinner=False)
def load_crop_dataset() -> pd.DataFrame:
    """Load the crop recommendation dataset."""
    return pd.read_csv(CROP_DATA_PATH, index_col=0)


@st.cache_data(show_spinner=False)
def load_production_dataset() -> pd.DataFrame:
    """Load and lightly clean the production dataset for UI dropdowns."""
    df = pd.read_csv(PRODUCTION_DATA_PATH)
    object_cols = df.select_dtypes(include=["object", "string"]).columns
    for col in object_cols:
        df[col] = df[col].astype(str).str.strip()
    return df


@st.cache_data(show_spinner=False)
def load_fertilizer_dataset() -> pd.DataFrame:
    """Load fertilizer lookup dataset."""
    return pd.read_csv(FERTILIZER_DATA_PATH, index_col=0)


@st.cache_data(show_spinner=False)
def load_crop_metrics() -> dict[str, Any]:
    """Load crop model evaluation metrics."""
    with CROP_METRICS_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


@st.cache_data(show_spinner=False)
def load_production_metrics() -> dict[str, Any]:
    """Load production model evaluation metrics."""
    with PRODUCTION_METRICS_PATH.open(encoding="utf-8") as handle:
        return json.load(handle)


@st.cache_resource(show_spinner=False)
def load_crop_artifacts() -> tuple[dict[str, Any], Any]:
    """Load crop model artifact bundle and label encoder."""
    artifact = joblib.load(CROP_MODEL_PATH)
    label_encoder = joblib.load(CROP_LABEL_ENCODER_PATH)
    return artifact, label_encoder


@st.cache_resource(show_spinner=False)
def load_production_artifacts() -> tuple[Any, Any]:
    """Load production regressor and preprocessor."""
    model = joblib.load(PRODUCTION_MODEL_PATH)
    preprocessor = joblib.load(PRODUCTION_PREPROCESSOR_PATH)
    return model, preprocessor


def get_crop_feature_ranges(df: pd.DataFrame) -> dict[str, tuple[float, float]]:
    """Return min/max ranges for crop feature sliders."""
    ranges: dict[str, tuple[float, float]] = {}
    for column in CROP_FEATURE_COLUMNS:
        ranges[column] = (float(df[column].min()), float(df[column].max()))
    return ranges


def get_production_options(df: pd.DataFrame) -> dict[str, list[Any]]:
    """Build sorted unique values for production form dropdowns."""
    return {
        "states": sorted(df["State_Name"].dropna().unique().tolist()),
        "years": sorted(df["Crop_Year"].dropna().unique().astype(int).tolist()),
        "seasons": sorted(df["Season"].dropna().unique().tolist()),
        "crops": sorted(df["Crop"].dropna().unique().tolist()),
    }


def get_districts_for_state(df: pd.DataFrame, state: str) -> list[str]:
    """Return districts available for a selected state."""
    if not state:
        return []
    districts = df.loc[df["State_Name"] == state, "District_Name"].dropna().unique()
    return sorted(districts.tolist())


def get_filtered_production_options(
    df: pd.DataFrame,
    state: str | None = None,
    district: str | None = None,
) -> dict[str, list[Any]]:
    """Filter seasons, crops, and years based on state/district selection."""
    filtered = df.copy()
    if state:
        filtered = filtered[filtered["State_Name"] == state]
    if district:
        filtered = filtered[filtered["District_Name"] == district]

    return {
        "years": sorted(filtered["Crop_Year"].dropna().unique().astype(int).tolist()),
        "seasons": sorted(filtered["Season"].dropna().unique().tolist()),
        "crops": sorted(filtered["Crop"].dropna().unique().tolist()),
    }


def get_reference_crop_year(
    df: pd.DataFrame,
    state: str,
    district: str,
    season: str,
    crop: str,
) -> int:
    """
    Return the most recent crop year for model inference.
    Uses the finest matching slice available in the historical dataset.
    """
    filtered = df[
        (df["State_Name"] == state)
        & (df["District_Name"] == district)
        & (df["Season"].str.strip() == season.strip())
        & (df["Crop"] == crop)
    ]
    if filtered.empty:
        filtered = df[(df["State_Name"] == state) & (df["District_Name"] == district)]
    if filtered.empty:
        filtered = df[df["State_Name"] == state]
    if filtered.empty:
        return int(df["Crop_Year"].max())
    return int(filtered["Crop_Year"].max())
