from pathlib import Path


# Project root folder
BASE_DIR = Path(__file__).resolve().parent.parent

# Data folders
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Data files
CV_RAW_DATA_PATH = RAW_DATA_DIR / "CVs.csv"
COST_RAW_DATA_PATH = RAW_DATA_DIR / "costs.csv"
ORDER_RAW_DATA_PATH = RAW_DATA_DIR / "orders.csv"
CV_PROCESSED_DATA_PATH = PROCESSED_DATA_DIR / "CVs_clean_data.csv"
COST_PROCESSED_DATA_PATH = PROCESSED_DATA_DIR / "costs_clean_data.csv"
ORDER_PROCESSED_DATA_PATH = PROCESSED_DATA_DIR / "orders_clean_data.csv"

# Model folder and file
MODELS_DIR = BASE_DIR / "models"
MODEL_PATH = MODELS_DIR / "recruitment_model.pkl"

# Environment file
ENV_PATH = BASE_DIR / ".env"