import joblib
import pandas as pd
from sqlalchemy import text

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from db import get_engine
from paths import MODEL_PATH, MODELS_DIR


TABLE_NAME = "hr_attrition"


def load_data_from_db() -> pd.DataFrame:
    engine = get_engine()
    query = text(f"SELECT * FROM {TABLE_NAME}")

    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    if df.empty:
        raise ValueError(
            f"Table `{TABLE_NAME}` không có dữ liệu. "
            "Hãy chạy `python src/upload_data.py` trước."
        )

    return df


def prepare_data(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    df = df.copy()

    if "Attrition" not in df.columns:
        raise ValueError("Không tìm thấy cột 'Attrition' trong dữ liệu.")

    drop_columns = [
        "EmployeeNumber",
        "EmployeeCount",
        "Over18",
        "StandardHours",
    ]

    existing_drop_columns = [
        col for col in drop_columns
        if col in df.columns
    ]

    df = df.drop(columns=existing_drop_columns)

    X = df.drop(columns=["Attrition"])
    y = df["Attrition"]

    return X, y


def build_model_pipeline(X: pd.DataFrame) -> Pipeline:
    categorical_features = X.select_dtypes(include=["object"]).columns.tolist()
    numerical_features = X.select_dtypes(include=["int64", "float64"]).columns.tolist()

    numeric_transformer = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
        ]
    )

    categorical_transformer = Pipeline(
        steps=[
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numerical_features),
            ("cat", categorical_transformer, categorical_features),
        ]
    )

    model = RandomForestClassifier(
        n_estimators=300,
        random_state=42,
        class_weight="balanced",
    )

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )

    return pipeline


def evaluate_model(
    pipeline: Pipeline,
    X_test: pd.DataFrame,
    y_test: pd.Series,
) -> None:
    y_pred = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)[:, 1]

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    roc_auc = roc_auc_score(y_test, y_proba)

    print("\n========== MODEL PERFORMANCE ==========")
    print(f"Accuracy : {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall   : {recall:.4f}")
    print(f"F1-score : {f1:.4f}")
    print(f"ROC-AUC  : {roc_auc:.4f}")

    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, zero_division=0))

    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))


def save_model(pipeline: Pipeline) -> None:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)

    print(f"\nModel saved to: {MODEL_PATH}")


def train_model() -> None:
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
        stratify=y,
    )

    print("Building model pipeline...")
    pipeline = build_model_pipeline(X)

    print("Training model...")
    pipeline.fit(X_train, y_train)

    print("Evaluating model...")
    evaluate_model(pipeline, X_test, y_test)

    print("Saving model...")
    save_model(pipeline)


def main() -> None:
    train_model()


if __name__ == "__main__":
    main()