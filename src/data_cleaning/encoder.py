from __future__ import annotations

import pandas as pd


def encode_features(
    df: pd.DataFrame,
    categorical_cols: list[str] | None = None,
    max_categories: int = 30,
    drop_first: bool = False,
) -> pd.DataFrame:
    """Optional One-Hot Encoding for selected categorical features.

    This function is intentionally not called by the Member 4 EDA pipeline:
    EDA should preserve original categories and readable text fields.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df phải là pandas DataFrame.")
    if max_categories < 1:
        raise ValueError("max_categories phải >= 1.")
    if not df.columns.is_unique:
        raise ValueError("Tên cột trong DataFrame phải là duy nhất trước khi encoding.")

    result = df.copy()
    if categorical_cols is None:
        candidates = result.select_dtypes(include=["object", "string", "category"]).columns
        excluded_tokens = (
            "name", "title", "author", "description", "blurb", "review",
            "link", "url", "isbn", "identifier", "_id", "id_",
        )
        categorical_cols = []
        for col in candidates:
            col_name = str(col).casefold()
            values = result[col].dropna().astype(str).str.strip()
            if any(token in col_name for token in excluded_tokens):
                continue
            if values.empty or values.str.len().mean() > 30:
                continue
            if values.str.contains(r"https?://|www\.", case=False, regex=True).any():
                continue
            if result[col].nunique(dropna=False) <= max_categories:
                categorical_cols.append(col)
    else:
        if len(categorical_cols) != len(set(categorical_cols)):
            raise ValueError("Danh sách categorical_cols có tên cột bị lặp.")
        missing_cols = [col for col in categorical_cols if col not in result.columns]
        if missing_cols:
            raise ValueError(f"Cột không tồn tại: {missing_cols}")
        wrong_type = [
            col for col in categorical_cols
            if not (pd.api.types.is_object_dtype(result[col])
                    or pd.api.types.is_string_dtype(result[col])
                    or isinstance(result[col].dtype, pd.CategoricalDtype))
        ]
        if wrong_type:
            raise TypeError(f"Cột được chọn không phải biến phân loại dạng chữ: {wrong_type}")
        too_many = [col for col in categorical_cols if result[col].nunique(dropna=False) > max_categories]
        if too_many:
            raise ValueError(f"Cột vượt quá max_categories={max_categories}: {too_many}")

    categorical_cols = [col for col in categorical_cols if result[col].nunique(dropna=False) > 1]
    if categorical_cols:
        result = pd.get_dummies(result, columns=categorical_cols, drop_first=drop_first, dtype=int)
    if not result.columns.is_unique:
        raise ValueError("Tên cột bị trùng sau encoding; hãy kiểm tra dữ liệu đầu vào.")
    return result
