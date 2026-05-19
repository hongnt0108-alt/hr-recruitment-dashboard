import shutil
from pathlib import Path

import kagglehub

from paths import RAW_DATA_DIR, RAW_DATA_PATH


DATASET_NAME = "pavansubhasht/ibm-hr-analytics-attrition-dataset"


def download_data() -> None:
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    dataset_dir = Path(kagglehub.dataset_download(DATASET_NAME))

    csv_files = list(dataset_dir.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(
            f"Không tìm thấy file CSV nào trong dataset đã tải: {dataset_dir}"
        )

    source_file = csv_files[0]

    shutil.copy(source_file, RAW_DATA_PATH)

    print(f"Dataset downloaded from: {source_file}")
    print(f"Dataset saved to: {RAW_DATA_PATH}")


def main() -> None:
    download_data()


if __name__ == "__main__":
    main()