import pandas as pd

from db import get_engine
from paths import (
    CV_PROCESSED_DATA_PATH,
    COST_PROCESSED_DATA_PATH,
    ORDER_PROCESSED_DATA_PATH,
)


TABLES = {
    "cvs": CV_PROCESSED_DATA_PATH,
    "costs": COST_PROCESSED_DATA_PATH,
    "orders": ORDER_PROCESSED_DATA_PATH,
}


def upload_file(table_name: str, file_path) -> None:
    if not file_path.exists():
        raise FileNotFoundError(
            f"Không tìm thấy file processed data tại: {file_path}. "
            "Hãy chạy `python src/clean_data.py` trước."
        )

    df = pd.read_csv(file_path)

    engine = get_engine()

    df.to_sql(
        table_name,
        engine,
        if_exists="replace",
        index=False,
    )

    print(f"Uploaded {len(df)} rows to table `{table_name}` successfully.")


def upload_data() -> None:
    for table_name, file_path in TABLES.items():
        upload_file(table_name, file_path)


def main() -> None:
    upload_data()


if __name__ == "__main__":
    main()