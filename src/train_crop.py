"""
Crop Recommendation training pipeline.

Trains and compares Random Forest, XGBoost, and CatBoost classifiers on
MergeFileCrop.csv, selects the best model by macro F1 score, and persists
artifacts for inference.
"""

from __future__ import annotations

import json
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "MergeFileCrop.csv"
MODELS_DIR = PROJECT_ROOT / "models"
MODEL_PATH = MODELS_DIR / "crop_model.pkl"
LABEL_ENCODER_PATH = MODELS_DIR / "crop_label_encoder.pkl"
METRICS_PATH = MODELS_DIR / "crop_training_metrics.json"

FEATURE_COLUMNS = ["temperature", "humidity", "ph", "rainfall"]
TARGET_COLUMN = "label"
RANDOM_STATE = 42
TEST_SIZE = 0.2


@dataclass
class ModelResult:
    name: str
    model: Any
    accuracy: float
    precision: float
    recall: float
    f1: float


def load_crop_data(path: Path = DATA_PATH) -> pd.DataFrame:
    """Load crop recommendation dataset."""
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")

    df = pd.read_csv(path, index_col=0)
    logger.info("Loaded dataset: %d rows, %d columns", df.shape[0], df.shape[1])
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Remove invalid rows and duplicates. Imputation is deferred until after split."""
    initial_rows = len(df)

    missing_features = df[FEATURE_COLUMNS].isnull().any(axis=1).sum()
    if missing_features > 0:
        logger.info(
            "Found %d rows with missing feature values (imputed after train-test split)",
            missing_features,
        )

    if df[TARGET_COLUMN].isnull().any():
        dropped_labels = df[TARGET_COLUMN].isnull().sum()
        df = df.dropna(subset=[TARGET_COLUMN])
        logger.info("Dropped %d rows with missing labels", dropped_labels)

    duplicates = df.duplicated().sum()
    if duplicates > 0:
        df = df.drop_duplicates()
        logger.info("Removed %d duplicate rows", duplicates)

    logger.info(
        "Cleaned dataset: %d -> %d rows",
        initial_rows,
        len(df),
    )
    return df.reset_index(drop=True)


def split_features_target(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.Series]:
    """Separate feature matrix and target vector."""
    missing_cols = [c for c in FEATURE_COLUMNS + [TARGET_COLUMN] if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Required columns missing from dataset: {missing_cols}")

    X = df[FEATURE_COLUMNS].copy()
    y = df[TARGET_COLUMN].copy()
    return X, y


def encode_labels(
    y_train: pd.Series,
    y_test: pd.Series,
) -> tuple[np.ndarray, np.ndarray, LabelEncoder]:
    """
    Fit label encoder on training labels only to prevent leakage.

    Unseen test labels raise an error rather than silently mis-encoding.
    """
    encoder = LabelEncoder()
    y_train_encoded = encoder.fit_transform(y_train)

    unknown_labels = set(y_test.unique()) - set(encoder.classes_)
    if unknown_labels:
        raise ValueError(
            f"Test set contains labels not seen during training: {unknown_labels}"
        )

    y_test_encoded = encoder.transform(y_test)
    logger.info("Encoded %d crop classes", len(encoder.classes_))
    return y_train_encoded, y_test_encoded, encoder


def build_models() -> dict[str, Any]:
    """Return classifier instances with sensible defaults."""
    return {
        "RandomForest": RandomForestClassifier(
            n_estimators=200,
            max_depth=None,
            min_samples_split=2,
            class_weight="balanced",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
        "XGBoost": XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.9,
            colsample_bytree=0.9,
            objective="multi:softprob",
            eval_metric="mlogloss",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
        "CatBoost": CatBoostClassifier(
            iterations=200,
            depth=6,
            learning_rate=0.1,
            loss_function="MultiClass",
            random_seed=RANDOM_STATE,
            verbose=0,
        ),
    }


def evaluate_model(
    name: str,
    model: Any,
    X_test: pd.DataFrame,
    y_test: np.ndarray,
) -> ModelResult:
    """Compute classification metrics on the held-out test set."""
    y_pred = model.predict(X_test)

    return ModelResult(
        name=name,
        model=model,
        accuracy=accuracy_score(y_test, y_pred),
        precision=precision_score(y_test, y_pred, average="macro", zero_division=0),
        recall=recall_score(y_test, y_pred, average="macro", zero_division=0),
        f1=f1_score(y_test, y_pred, average="macro", zero_division=0),
    )


def train_and_compare(
    X_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_train: np.ndarray,
    y_test: np.ndarray,
) -> list[ModelResult]:
    """Train all candidate models and evaluate on the test split."""
    results: list[ModelResult] = []

    for name, model in build_models().items():
        logger.info("Training %s...", name)
        model.fit(X_train, y_train)
        result = evaluate_model(name, model, X_test, y_test)
        results.append(result)
        logger.info(
            "%s | Accuracy: %.4f | Precision: %.4f | Recall: %.4f | F1: %.4f",
            name,
            result.accuracy,
            result.precision,
            result.recall,
            result.f1,
        )

    return results


def select_best_model(results: list[ModelResult]) -> ModelResult:
    """
    Select the best model by macro F1, then accuracy as tiebreaker.
    """
    best = max(results, key=lambda r: (r.f1, r.accuracy))
    logger.info("Best model: %s (F1=%.4f, Accuracy=%.4f)", best.name, best.f1, best.accuracy)
    return best


def save_artifacts(
    model: Any,
    label_encoder: LabelEncoder,
    imputer: SimpleImputer,
    metrics: dict[str, Any],
) -> None:
    """Persist trained model, label encoder, and evaluation metrics."""
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    artifact = {
        "model": model,
        "imputer": imputer,
        "feature_columns": FEATURE_COLUMNS,
        "target_column": TARGET_COLUMN,
    }
    joblib.dump(artifact, MODEL_PATH)
    joblib.dump(label_encoder, LABEL_ENCODER_PATH)

    with METRICS_PATH.open("w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    logger.info("Saved model to %s", MODEL_PATH)
    logger.info("Saved label encoder to %s", LABEL_ENCODER_PATH)
    logger.info("Saved metrics to %s", METRICS_PATH)


def run_pipeline() -> ModelResult:
    """Execute the full crop recommendation training pipeline."""
    df = load_crop_data()
    df = clean_data(df)
    X, y = split_features_target(df)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )
    logger.info(
        "Train-test split: train=%d, test=%d (test_size=%.0f%%)",
        len(X_train),
        len(X_test),
        TEST_SIZE * 100,
    )

    y_train_enc, y_test_enc, label_encoder = encode_labels(y_train, y_test)

    train_imputer = SimpleImputer(strategy="median")
    X_train_imputed = pd.DataFrame(
        train_imputer.fit_transform(X_train),
        columns=FEATURE_COLUMNS,
        index=X_train.index,
    )
    X_test_imputed = pd.DataFrame(
        train_imputer.transform(X_test),
        columns=FEATURE_COLUMNS,
        index=X_test.index,
    )

    results = train_and_compare(X_train_imputed, X_test_imputed, y_train_enc, y_test_enc)
    best = select_best_model(results)

    metrics = {
        "best_model": best.name,
        "selection_metric": "macro_f1",
        "test_size": TEST_SIZE,
        "random_state": RANDOM_STATE,
        "feature_columns": FEATURE_COLUMNS,
        "n_classes": len(label_encoder.classes_),
        "class_labels": label_encoder.classes_.tolist(),
        "models": {
            r.name: {
                "accuracy": round(r.accuracy, 4),
                "precision_macro": round(r.precision, 4),
                "recall_macro": round(r.recall, 4),
                "f1_macro": round(r.f1, 4),
            }
            for r in results
        },
    }
    save_artifacts(best.model, label_encoder, train_imputer, metrics)

    return best


def main() -> int:
    try:
        best = run_pipeline()
        print(
            f"\nTraining complete. Best model: {best.name} "
            f"(F1={best.f1:.4f}, Accuracy={best.accuracy:.4f})"
        )
        return 0
    except Exception:
        logger.exception("Crop training pipeline failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
