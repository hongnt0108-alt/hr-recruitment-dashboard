import pandas as pd

from paths import PROCESSED_DATA_PATH, RAW_DATA_PATH


def clean_data() -> None:
    if not RAW_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Không tìm thấy file raw data tại: {RAW_DATA_PATH}. "
            "Hãy chạy `python src/download_data.py` trước."
        )

    df = pd.read_csv(RAW_DATA_PATH)

    if "Attrition" not in df.columns:
        raise ValueError("Không tìm thấy cột 'Attrition' trong dataset.")

    df["Attrition"] = df["Attrition"].map({"Yes": 1, "No": 0})

    PROCESSED_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(PROCESSED_DATA_PATH, index=False)

    print(f"Clean data saved to: {PROCESSED_DATA_PATH}")


def main() -> None:
    clean_data()


if __name__ == "__main__":
    main()