from pathlib import Path


# Project root folder
BASE_DIR = Path(__file__).resolve().parent.parent

# Data folders
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Data files
RAW_DATA_PATH = RAW_DATA_DIR / "WA_Fn-UseC_-HR-Employee-Attrition.csv"
PROCESSED_DATA_PATH = PROCESSED_DATA_DIR / "clean_data.csv"

# Model folder and file
MODELS_DIR = BASE_DIR / "models"
MODEL_PATH = MODELS_DIR / "attrition_model.pkl"

# Environment file
ENV_PATH = BASE_DIR / ".env"