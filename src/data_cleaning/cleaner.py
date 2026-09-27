import numpy as np
import pandas as pd


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Xóa dòng trùng, chuyển giá trị lỗi thành NaN và điền dữ liệu khuyết."""
    # 1. Xóa dòng trùng lặp
    df = df.drop_duplicates()

    # 2. Thay thế giá trị lỗi thành NaN
    invalid_values = ["ERROR", "UNKNOWN", "N/A", "null", "None"]
    df = df.replace(invalid_values, np.nan)

    # 3. Điền giá trị thiếu (NaN)
    for col in df.columns:
        if df[col].dtype in ["int64", "float64"]:
            df[col] = df[col].fillna(df[col].median())
        else:
            df[col] = df[col].fillna("Unknown")

    return df