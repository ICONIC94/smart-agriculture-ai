"""Application configuration and path constants."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"

CROP_DATA_PATH = DATA_DIR / "MergeFileCrop.csv"
PRODUCTION_DATA_PATH = DATA_DIR / "raw_districtwise_yield_data.csv"
FERTILIZER_DATA_PATH = DATA_DIR / "Fertilizer.csv"

CROP_MODEL_PATH = MODELS_DIR / "crop_model.pkl"
CROP_LABEL_ENCODER_PATH = MODELS_DIR / "crop_label_encoder.pkl"
CROP_METRICS_PATH = MODELS_DIR / "crop_training_metrics.json"

PRODUCTION_MODEL_PATH = MODELS_DIR / "production_model.pkl"
PRODUCTION_PREPROCESSOR_PATH = MODELS_DIR / "production_preprocessor.pkl"
PRODUCTION_METRICS_PATH = MODELS_DIR / "production_metrics.json"

APP_TITLE = "AgriSense AI"
APP_SUBTITLE = "Smart Agriculture Platform"

CROP_FEATURE_COLUMNS = ["temperature", "humidity", "ph", "rainfall"]

PRODUCTION_COLUMNS = [
    "State_Name",
    "District_Name",
    "Crop_Year",
    "Season",
    "Crop",
    "Area",
]

NAV_ITEMS = [
    ("home", "Home", "house"),
    ("crop", "🌱 Crop Recommendation", "seedling"),
    ("production", "Production Prediction", "graph-up"),
    ("fertilizer", "Fertilizer Recommendation", "droplet"),
    ("about", "About", "info-circle"),
]
