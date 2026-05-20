import pandas as pd

from paths import (
    CV_RAW_DATA_PATH,
    COST_RAW_DATA_PATH,
    ORDER_RAW_DATA_PATH,
    CV_PROCESSED_DATA_PATH,
    COST_PROCESSED_DATA_PATH,
    ORDER_PROCESSED_DATA_PATH,
)


def read_csv_clean_columns(path):
    """
    Đọc file CSV và làm sạch:
    - Xóa khoảng trắng thừa ở tên cột
    - Xóa các cột không có title / Unnamed
    - Xóa các dòng rỗng hoàn toàn
    """
    df = pd.read_csv(path)

    # Xóa khoảng trắng thừa ở tên cột
    df.columns = df.columns.astype(str).str.strip()

    # Xóa các cột không có title hoặc cột thừa từ Excel/CSV
    valid_columns = [
        col for col in df.columns
        if col
        and not col.lower().startswith("unnamed")
        and col.lower() not in ["nan", "none", "null"]
    ]

    df = df[valid_columns]

    # Chuẩn hóa dữ liệu text: xóa khoảng trắng thừa
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    # Đổi các ô text rỗng thành NA
    df = df.replace(["", " ", "nan", "NaN", "None", "NONE", "null", "NULL"], pd.NA)

    # Xóa các dòng rỗng hoàn toàn
    df = df.dropna(how="all")

    # Reset lại index sau khi xóa dòng
    df = df.reset_index(drop=True)

    return df


def normalize_base_order_id(series: pd.Series) -> pd.Series:
    """
    Chuẩn hóa BaseOrder ID để merge được giữa các file.

    Xử lý các trường hợp:
    - 1001.0 -> 1001
    - " 1001 " -> "1001"
    - "1001\n" -> "1001"
    - nan / NaN / None / null -> ""
    """
    return (
        series
        .astype(str)
        .str.strip()
        .str.replace(r"\.0$", "", regex=True)
        .str.replace(r"\s+", "", regex=True)
        .replace(["nan", "NaN", "None", "NONE", "null", "NULL"], "")
    )


def add_department_from_orders(df, orders_df, file_name=""):
    """
    Add cột 'Phòng ban' vào df dựa trên orders_df.

    Key:
    df['BaseOrder ID'] = orders_df['BaseOrder ID']

    Áp dụng cho:
    - CVs_clean_data.csv
    - costs_clean_data.csv
    """
    df = df.copy()
    orders_df = orders_df.copy()

    # Làm sạch tên cột thêm lần nữa cho chắc
    df.columns = df.columns.astype(str).str.strip()
    orders_df.columns = orders_df.columns.astype(str).str.strip()

    key_col = "BaseOrder ID"
    department_col = "Phòng ban"
    merge_key_col = "_merge_base_order_id"

    if key_col not in df.columns:
        print(f"[{file_name}] Không tìm thấy cột '{key_col}' trong file cần xử lý")
        return df

    if key_col not in orders_df.columns:
        print(f"[orders] Không tìm thấy cột '{key_col}' trong orders.csv")
        return df

    if department_col not in orders_df.columns:
        print(f"[orders] Không tìm thấy cột '{department_col}' trong orders.csv")
        return df

    # Tạo key phụ để merge, không làm hỏng cột gốc
    df[merge_key_col] = normalize_base_order_id(df[key_col])
    orders_df[merge_key_col] = normalize_base_order_id(orders_df[key_col])

    # Bảng lookup: BaseOrder ID -> Phòng ban
    department_lookup = (
        orders_df[[merge_key_col, department_col]]
        .dropna(subset=[merge_key_col])
        .drop_duplicates(subset=[merge_key_col])
    )

    # Nếu df đã có cột Phòng ban thì xóa để lấy lại từ orders_df
    if department_col in df.columns:
        df = df.drop(columns=[department_col])

    # Merge Phòng ban vào df
    df = df.merge(
        department_lookup,
        on=merge_key_col,
        how="left"
    )

    # Xóa key phụ sau khi merge
    df = df.drop(columns=[merge_key_col])

    # Debug kết quả mapping
    missing_count = df[department_col].isna().sum()
    total_count = len(df)

    print(f"[{file_name}] Số dòng chưa map được Phòng ban: {missing_count}/{total_count}")

    if missing_count > 0:
        print(f"[{file_name}] Một vài BaseOrder ID chưa map được:")
        print(
            df.loc[df[department_col].isna(), key_col]
            .dropna()
            .head(10)
            .tolist()
        )

    return df


def clean_data() -> None:
    raw_paths = [
        CV_RAW_DATA_PATH,
        COST_RAW_DATA_PATH,
        ORDER_RAW_DATA_PATH,
    ]

    # Kiểm tra file raw có tồn tại không
    for raw_path in raw_paths:
        if not raw_path.exists():
            raise FileNotFoundError(
                f"Không tìm thấy file raw data tại: {raw_path}. "
                "Hãy kiểm tra lại thư mục data/raw."
            )

    # Đọc và làm sạch cột
    orders_df = read_csv_clean_columns(ORDER_RAW_DATA_PATH)
    cvs_df = read_csv_clean_columns(CV_RAW_DATA_PATH)
    costs_df = read_csv_clean_columns(COST_RAW_DATA_PATH)

    # Add cột Phòng ban vào CVs và Costs dựa trên BaseOrder ID
    cvs_df = add_department_from_orders(
        cvs_df,
        orders_df,
        file_name="CVs"
    )

    costs_df = add_department_from_orders(
        costs_df,
        orders_df,
        file_name="Costs"
    )

    # Danh sách file processed cần lưu
    processed_files = {
        ORDER_PROCESSED_DATA_PATH: orders_df,
        CV_PROCESSED_DATA_PATH: cvs_df,
        COST_PROCESSED_DATA_PATH: costs_df,
    }

    # Lưu file processed
    for processed_path, df in processed_files.items():
        processed_path.parent.mkdir(parents=True, exist_ok=True)

        df.to_csv(
            processed_path,
            index=False,
            encoding="utf-8-sig"
        )

        print(f"Saved processed data to: {processed_path}")


def main() -> None:
    clean_data()


if __name__ == "__main__":
    main()