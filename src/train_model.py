import sys
from pathlib import Path

import joblib
import pandas as pd

from sqlalchemy import text

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    classification_report,
    confusion_matrix
)


# =========================
# PATH SETUP
# =========================

BASE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = BASE_DIR / "src"
MODELS_DIR = BASE_DIR / "models"

sys.path.append(str(SRC_DIR))

from db import get_engine


# =========================
# LOAD DATA FROM POSTGRESQL
# =========================

def load_data_from_db():
    engine = get_engine()

    query = text("SELECT * FROM hr_attrition")

    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    return df

# =========================
# PREPARE DATA
# =========================

def prepare_data(df):
    df = df.copy()

    # Bỏ các cột không nên dùng để train
    drop_columns = [
        "EmployeeNumber",
        "EmployeeCount",
        "Over18",
        "StandardHours"
    ]

    existing_drop_columns = [
        col for col in drop_columns
        if col in df.columns
    ]

    df = df.drop(columns=existing_drop_columns)

    # Tách X và y
    X = df.drop(columns=["Attrition"])
    y = df["Attrition"]
    return X, y

# # =========================
# # BUILD MODEL PIPELINE
# # =========================

def build_model_pipeline(X):
    categorical_features = X.select_dtypes(include=["object"]).columns.tolist()
    numerical_features = X.select_dtypes(include=["int64", "float64"]).columns.tolist()

    numeric_transformer = Pipeline(
        steps=[
            ("scaler", StandardScaler())
        ]
    )

    categorical_transformer = Pipeline(
        steps=[
            ("onehot", OneHotEncoder(handle_unknown="ignore"))
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numerical_features),
            ("cat", categorical_transformer, categorical_features)
        ]
    )

    model = RandomForestClassifier(
        n_estimators=300,
        random_state=42,
        class_weight="balanced"
    )

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model)
        ]
    )

    return pipeline


# =========================
# TRAIN + EVALUATE + SAVE
# =========================

def train_model():
    print("Loading data from PostgreSQL...")
    df = load_data_from_db()

    print("Preparing data...")
    X, y = prepare_data(df)

    print("Splitting train/test data...")
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    print("Building model pipeline...")
    pipeline = build_model_pipeline(X)

    print("Training model...")
    pipeline.fit(X_train, y_train)

    print("Evaluating model...")
    y_pred = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)[:, 1]

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_proba)

    print("\n========== MODEL PERFORMANCE ==========")
    print(f"Accuracy : {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall   : {recall:.4f}")
    print(f"F1-score : {f1:.4f}")
    print(f"ROC-AUC  : {roc_auc:.4f}")

    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    print("\nSaving model...")
    MODELS_DIR.mkdir(exist_ok=True)

    model_path = MODELS_DIR / "attrition_model.pkl"
    joblib.dump(pipeline, model_path)

    print(f"Model saved to: {model_path}")


if __name__ == "__main__":
    train_model()