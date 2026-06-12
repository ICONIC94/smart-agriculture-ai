"""
Production prediction training pipeline.

Trains and compares Random Forest, XGBoost, and CatBoost regressors on
raw_districtwise_yield_data.csv, selects the best model by R² score,
and persists artifacts for inference.
"""

from __future__ import annotations

import json
import logging
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from catboost import CatBoostRegressor
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from xgboost import XGBRegressor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "raw_districtwise_yield_data.csv"
MODELS_DIR = PROJECT_ROOT / "models"
MODEL_PATH = MODELS_DIR / "production_model.pkl"
PREPROCESSOR_PATH = MODELS_DIR / "production_preprocessor.pkl"
METRICS_PATH = MODELS_DIR / "production_metrics.json"

TARGET_COLUMN = "Production"
RANDOM_STATE = 42
TEST_SIZE = 0.2

# Canonical feature names mapped to likely column aliases in the dataset.
FEATURE_ALIASES: dict[str, list[str]] = {
    "state": ["state_name", "state"],
    "district": ["district_name", "district"],
    "crop_year": ["crop_year", "year", "cropyear"],
    "season": ["season"],
    "crop": ["crop", "crop_name"],
    "area": ["area", "area_hectares", "area_ha"],
}


@dataclass
class ModelResult:
    """Container for a trained regressor and its evaluation metrics."""

    name: str
    model: Any
    rmse: float
    mae: float
    r2: float


def _normalize_column_name(name: str) -> str:
    """Normalize a column name for fuzzy matching."""
    return re.sub(r"[^a-z0-9]", "", name.strip().lower())


def _find_target_column(columns: list[str]) -> str:
    """Locate the Production target column regardless of casing/spacing."""
    for col in columns:
        if _normalize_column_name(col) == "production":
            return col
    raise ValueError(
        f"Target column '{TARGET_COLUMN}' not found. Available columns: {columns}"
    )


def resolve_feature_columns(columns: list[str], target_col: str) -> dict[str, str]:
    """
    Map canonical feature names to actual dataset column names.

    Returns a dict of canonical_name -> actual_column_name.
    """
    normalized = {_normalize_column_name(c): c for c in columns}
    resolved: dict[str, str] = {}

    for canonical, aliases in FEATURE_ALIASES.items():
        for alias in aliases:
            norm_alias = _normalize_column_name(alias)
            if norm_alias in normalized:
                resolved[canonical] = normalized[norm_alias]
                break

    if not resolved:
        raise ValueError(
            f"No recognised feature columns found. Available columns: {columns}"
        )

    # Include any remaining non-target columns not yet mapped.
    used = set(resolved.values()) | {target_col}
    for col in columns:
        if col not in used:
            key = _normalize_column_name(col)
            if key not in resolved:
                resolved[key] = col

    logger.info("Resolved feature columns: %s", resolved)
    return resolved


def load_data(path: Path = DATA_PATH) -> pd.DataFrame:
    """Load the district-wise yield dataset."""
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")

    df = pd.read_csv(path)
    if df.empty:
        raise ValueError("Dataset is empty after loading.")

    logger.info("Loaded dataset: %d rows, %d columns", df.shape[0], df.shape[1])
    logger.info("Columns: %s", df.columns.tolist())
    logger.info("Dtypes:\n%s", df.dtypes.to_string())
    logger.info("Missing values:\n%s", df.isnull().sum().to_string())
    logger.info("Duplicate rows: %d", df.duplicated().sum())
    return df


def clean_data(df: pd.DataFrame) -> tuple[pd.DataFrame, str, list[str], list[str]]:
    """
    Clean raw data and identify feature / target columns.

    Returns cleaned dataframe, target column name, numeric feature columns,
    and categorical feature columns.
    """
    initial_rows = len(df)
    df = df.copy()

    # Strip whitespace from object columns.
    object_cols = df.select_dtypes(include=["object", "string"]).columns
    for col in object_cols:
        df[col] = df[col].astype(str).str.strip()
        df[col] = df[col].replace({"nan": np.nan, "": np.nan, "None": np.nan})

    target_col = _find_target_column(df.columns.tolist())
    feature_map = resolve_feature_columns(df.columns.tolist(), target_col)
    feature_cols = [feature_map[k] for k in sorted(feature_map)]

    # Drop rows with missing target — cannot supervise without Production.
    missing_target = df[target_col].isnull().sum()
    if missing_target > 0:
        df = df.dropna(subset=[target_col])
        logger.info("Dropped %d rows with missing target '%s'", missing_target, target_col)

    # Coerce numeric-looking columns.
    for col in feature_cols:
        if col not in df.columns:
            continue
        if df[col].dtype == object:
            converted = pd.to_numeric(df[col], errors="coerce")
            if converted.notna().sum() > 0.9 * len(df):
                df[col] = converted
                logger.info("Coerced column '%s' to numeric", col)

    # Remove duplicate rows.
    duplicates = df.duplicated().sum()
    if duplicates > 0:
        df = df.drop_duplicates()
        logger.info("Removed %d duplicate rows", duplicates)

    if df.empty:
        raise ValueError("Dataset is empty after cleaning.")

    # Classify features for preprocessing.
    numeric_features: list[str] = []
    categorical_features: list[str] = []
    for col in feature_cols:
        if col not in df.columns:
            continue
        if pd.api.types.is_numeric_dtype(df[col]):
            numeric_features.append(col)
        else:
            categorical_features.append(col)

    logger.info(
        "Cleaned dataset: %d -> %d rows | numeric=%s | categorical=%s",
        initial_rows,
        len(df),
        numeric_features,
        categorical_features,
    )
    return df.reset_index(drop=True), target_col, numeric_features, categorical_features


def build_preprocessor(
    numeric_features: list[str],
    categorical_features: list[str],
) -> ColumnTransformer:
    """Build a sklearn preprocessing pipeline for numeric and categorical features."""
    transformers: list[tuple[str, Pipeline, list[str]]] = []

    if numeric_features:
        numeric_pipeline = Pipeline(
            steps=[("imputer", SimpleImputer(strategy="median"))]
        )
        transformers.append(("num", numeric_pipeline, numeric_features))

    if categorical_features:
        try:
            encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=True)
        except TypeError:
            encoder = OneHotEncoder(handle_unknown="ignore", sparse=True)

        categorical_pipeline = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("encoder", encoder),
            ]
        )
        transformers.append(("cat", categorical_pipeline, categorical_features))

    if not transformers:
        raise ValueError("No features available for preprocessing.")

    return ColumnTransformer(transformers=transformers, remainder="drop")


def _ensure_dense(X: Any, model_name: str) -> Any:
    """Convert sparse feature matrices to dense for models that require it."""
    if model_name == "CatBoost" and hasattr(X, "toarray"):
        return X.toarray()
    return X


def build_models() -> dict[str, Any]:
    """Return regressor instances with sensible defaults."""
    return {
        "RandomForest": RandomForestRegressor(
            n_estimators=50,
            max_depth=20,
            min_samples_split=5,
            max_samples=0.3,
            max_features="sqrt",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
        "XGBoost": XGBRegressor(
            n_estimators=100,
            max_depth=8,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            objective="reg:squarederror",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
        "CatBoost": CatBoostRegressor(
            iterations=100,
            depth=8,
            learning_rate=0.1,
            loss_function="RMSE",
            random_seed=RANDOM_STATE,
            verbose=0,
        ),
    }


def train_models(
    models: dict[str, Any],
    X_train: np.ndarray,
    y_train: pd.Series,
) -> dict[str, Any]:
    """Fit all candidate regressors on preprocessed training data."""
    trained: dict[str, Any] = {}
    for name, model in models.items():
        logger.info("Training %s...", name)
        X_fit = _ensure_dense(X_train, name)
        model.fit(X_fit, y_train)
        trained[name] = model
    return trained


def evaluate_models(
    trained_models: dict[str, Any],
    X_test: np.ndarray,
    y_test: pd.Series,
) -> list[ModelResult]:
    """Compute RMSE, MAE, and R² for each trained model."""
    results: list[ModelResult] = []

    for name, model in trained_models.items():
        X_eval = _ensure_dense(X_test, name)
        y_pred = model.predict(X_eval)
        rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
        mae = float(mean_absolute_error(y_test, y_pred))
        r2 = float(r2_score(y_test, y_pred))

        result = ModelResult(name=name, model=model, rmse=rmse, mae=mae, r2=r2)
        results.append(result)
        logger.info(
            "%s | RMSE: %.4f | MAE: %.4f | R²: %.4f",
            name,
            rmse,
            mae,
            r2,
        )

    return results


def select_best_model(results: list[ModelResult]) -> ModelResult:
    """Select the best model by highest R², then lowest RMSE as tiebreaker."""
    best = max(results, key=lambda r: (r.r2, -r.rmse))
    logger.info(
        "Best model: %s (R²=%.4f, RMSE=%.4f, MAE=%.4f)",
        best.name,
        best.r2,
        best.rmse,
        best.mae,
    )
    return best


def save_artifacts(
    model: Any,
    preprocessor: ColumnTransformer,
    metrics: dict[str, Any],
) -> None:
    """Persist trained model, preprocessor, and evaluation metrics."""
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    joblib.dump(model, MODEL_PATH)
    joblib.dump(preprocessor, PREPROCESSOR_PATH)

    with METRICS_PATH.open("w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    logger.info("Saved model to %s", MODEL_PATH)
    logger.info("Saved preprocessor to %s", PREPROCESSOR_PATH)
    logger.info("Saved metrics to %s", METRICS_PATH)


def run_pipeline() -> ModelResult:
    """Execute the full production prediction training pipeline."""
    df = load_data()
    df, target_col, numeric_features, categorical_features = clean_data(df)

    feature_cols = numeric_features + categorical_features
    X = df[feature_cols]
    y = df[target_col]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
    )
    logger.info(
        "Train-test split: train=%d, test=%d (test_size=%.0f%%)",
        len(X_train),
        len(X_test),
        TEST_SIZE * 100,
    )

    preprocessor = build_preprocessor(numeric_features, categorical_features)
    X_train_processed = preprocessor.fit_transform(X_train)
    X_test_processed = preprocessor.transform(X_test)
    logger.info(
        "Preprocessed feature matrix shape: train=%s, test=%s",
        X_train_processed.shape,
        X_test_processed.shape,
    )

    trained = train_models(build_models(), X_train_processed, y_train)
    results = evaluate_models(trained, X_test_processed, y_test)
    best = select_best_model(results)

    metrics = {
        "best_model": best.name,
        "selection_metric": "r2",
        "test_size": TEST_SIZE,
        "random_state": RANDOM_STATE,
        "target_column": target_col,
        "numeric_features": numeric_features,
        "categorical_features": categorical_features,
        "dataset_shape_after_cleaning": list(df.shape),
        "models": {
            r.name: {
                "rmse": round(r.rmse, 4),
                "mae": round(r.mae, 4),
                "r2": round(r.r2, 4),
            }
            for r in results
        },
    }
    save_artifacts(best.model, preprocessor, metrics)
    return best


def main() -> int:
    """Entry point for the production prediction training pipeline."""
    try:
        best = run_pipeline()
        print(
            f"\nTraining complete. Best model: {best.name} "
            f"(R²={best.r2:.4f}, RMSE={best.rmse:.4f}, MAE={best.mae:.4f})"
        )
        return 0
    except (FileNotFoundError, ValueError) as exc:
        logger.error("%s", exc)
        return 1
    except Exception:
        logger.exception("Production training pipeline failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
