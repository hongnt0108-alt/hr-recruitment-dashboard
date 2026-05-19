import pandas as pd

from db import get_engine
from paths import PROCESSED_DATA_PATH


TABLE_NAME = "hr_attrition"


def upload_data() -> None:
    if not PROCESSED_DATA_PATH.exists():
        raise FileNotFoundError(
            f"Không tìm thấy file processed data tại: {PROCESSED_DATA_PATH}. "
            "Hãy chạy `python src/clean_data.py` trước."
        )

    df = pd.read_csv(PROCESSED_DATA_PATH)

    engine = get_engine()

    df.to_sql(
        TABLE_NAME,
        engine,
        if_exists="replace",
        index=False,
    )

    print(f"Uploaded {len(df)} rows to table `{TABLE_NAME}` successfully.")


def main() -> None:
    upload_data()


if __name__ == "__main__":
    main()