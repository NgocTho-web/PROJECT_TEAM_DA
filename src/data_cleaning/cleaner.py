
from __future__ import annotations

import re
import warnings

import numpy as np
import pandas as pd


INVALID_VALUES = {
    "error", "unknown", "n/a", "na", "null", "none", "nan"
}

# Cột định danh: không tự điền giá trị giả.
ID_PATTERN = re.compile(r"(^|[_\s\-])id($|[_\s\-])")
IDENTIFIER_TOKENS = (
    "isbn", "identifier", "uuid", "code", "url", "link"
)

# Văn bản tự do, tên sách, tên tác giả...
TEXT_TOKENS = (
    "name", "title", "author", "description", "blurb",
    "review", "summary", "comment", "content", "subtitle"
)

# Các tên cột có thể chứa ngày tháng.
DATE_TOKENS = (
    "date", "timestamp", "created", "updated",
    "published", "datetime"
)


def is_identifier_col(col: str) -> bool:
    """Nhận diện cột định danh."""
    name = str(col).casefold()

    # Xử lý cả ID, product_id, productID, bookId...
    compact = re.sub(r"[^a-z0-9]", "", name)

    return (
        bool(ID_PATTERN.search(name))
        or compact == "id"
        or compact.endswith("id")
        or any(token in name for token in IDENTIFIER_TOKENS)
    )


def is_free_text_col(col: str) -> bool:
    """Nhận diện cột văn bản tự do hoặc tên riêng."""
    name = str(col).casefold()
    return any(token in name for token in TEXT_TOKENS)


def is_date_name(col: str) -> bool:
    """Nhận diện cột có tên gợi ý ngày/thời gian."""
    name = str(col).casefold()
    return any(token in name for token in DATE_TOKENS)


def normalize_missing_tokens(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Chuẩn hóa token lỗi và chuỗi rỗng thành NaN.
    Không thay đổi DataFrame đầu vào.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df phải là pandas DataFrame.")

    result = df.copy()

    for col in result.select_dtypes(
        include=["object", "string"]
    ).columns:
        text = result[col].astype("string").str.strip()

        invalid = (
            text.str.casefold().isin(INVALID_VALUES)
            | text.eq("")
        ).fillna(False)

        result.loc[invalid, col] = np.nan

        # Loại bỏ khoảng trắng thừa ở các giá trị văn bản.
        result[col] = result[col].map(
            lambda value: (
                value.strip() if isinstance(value, str)
                else value
            )
        )

    return result


def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Chuẩn hóa dữ liệu, xóa dòng trùng, nhận diện kiểu dữ liệu.
    Chưa thực hiện imputation.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df phải là pandas DataFrame.")

    if not df.columns.is_unique:
        raise ValueError(
            "Dataset có tên cột trùng. "
            "Hãy xử lý tên cột trước khi làm sạch."
        )

    result = (
        normalize_missing_tokens(df)
        .drop_duplicates()
        .reset_index(drop=True)
    )

    for col in result.select_dtypes(
        include=["object", "string"]
    ).columns:
        non_missing = result[col].dropna()

        # Ngày tháng: không ép kiểu cột ID hoặc văn bản.
        if is_date_name(col):
            if non_missing.empty:
                result[col] = pd.to_datetime(
                    result[col], errors="coerce"
                )
                continue

            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                parsed = pd.to_datetime(
                    non_missing, errors="coerce"
                )

            # Chỉ chuyển thành datetime khi phần lớn giá trị
            # có thể được đọc là ngày tháng.
            if parsed.notna().mean() >= 0.8:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    result[col] = pd.to_datetime(
                        result[col], errors="coerce"
                    )
            continue

        # Không ép kiểu định danh hoặc văn bản tự do.
        if (
            is_identifier_col(col)
            or is_free_text_col(col)
            or non_missing.empty
        ):
            continue

        # Chuyển sang số nếu tất cả giá trị hợp lệ đều là số.
        numeric = pd.to_numeric(
            non_missing, errors="coerce"
        )

        if numeric.notna().all():
            result[col] = pd.to_numeric(
                result[col], errors="coerce"
            )

    # Thay vô cực bằng NaN để xử lý như giá trị thiếu.
    for col in result.select_dtypes(
        include=["number"]
    ).columns:
        result[col] = result[col].replace(
            [np.inf, -np.inf], np.nan
        )

    return result


def impute_missing(
    df: pd.DataFrame,
    categorical_max: int = 30,
    skew_threshold: float = 0.5,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Điền giá trị thiếu theo từng loại cột.

    - Cột định danh: giữ thiếu, không tạo ID giả.
    - Cột ngày: giữ NaT, không nội suy tự động.
    - Cột số: mean nếu gần đối xứng, median nếu lệch.
    - Cột boolean: mode.
    - Văn bản tự do: Unknown.
    - Phân loại ít nhóm: mode.
    - Phân loại nhiều nhóm: Unknown.

    Trả về (DataFrame sau xử lý, imputation_log).
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df phải là pandas DataFrame.")

    if categorical_max < 1:
        raise ValueError("categorical_max phải >= 1.")

    if skew_threshold < 0:
        raise ValueError("skew_threshold phải >= 0.")

    result = df.copy()
    log: list[dict] = []

    def add(
        col,
        strategy,
        n_missing,
        fill_value,
        reason,
    ):
        log.append({
            "column": col,
            "dtype": str(result[col].dtype),
            "missing_count": int(n_missing),
            "strategy": strategy,
            "fill_value": fill_value,
            "reason": reason,
        })

    for col in result.columns:
        series = result[col]
        n_missing = int(series.isna().sum())

        if n_missing == 0:
            continue

        # 1. Cột định danh: không điền giá trị giả.
        if is_identifier_col(col):
            add(
                col,
                "skip",
                n_missing,
                "",
                "Cột định danh: giữ giá trị thiếu",
            )
            continue

        # 2. Cột ngày xuất bản: không nội suy ngày giả.
        if pd.api.types.is_datetime64_any_dtype(series):
            add(
                col,
                "skip",
                n_missing,
                "",
                "Cột ngày/thời gian; không tự động nội suy "
                "vì dữ liệu sách không mặc định là chuỗi thời gian",
            )
            continue

        # 3. Biến boolean.
        if pd.api.types.is_bool_dtype(series):
            modes = series.mode(dropna=True)

            if modes.empty:
                add(
                    col, "skip", n_missing, "",
                    "Không có giá trị hợp lệ để xác định mode",
                )
            else:
                fill = modes.iloc[0]
                result[col] = series.fillna(fill)
                add(
                    col, "mode", n_missing, fill,
                    "Biến boolean; điền giá trị phổ biến nhất",
                )
            continue

        # 4. Biến số.
        if pd.api.types.is_numeric_dtype(series):
            valid = series.dropna()

            if valid.empty:
                add(
                    col,
                    "skip",
                    n_missing,
                    "",
                    "Toàn bộ giá trị thiếu; giữ NaN",
                )
                continue

            skew = valid.skew()

            if (
                pd.notna(skew)
                and abs(skew) < skew_threshold
            ):
                fill = valid.mean()
                strategy = "mean"
                reason = (
                    f"skew={skew:.2f}; "
                    "phân phối gần đối xứng"
                )
            else:
                fill = valid.median()
                strategy = "median"

                if pd.isna(skew):
                    reason = (
                        "Không xác định được skew; "
                        "dùng median"
                    )
                else:
                    reason = (
                        f"skew={skew:.2f}; "
                        "phân phối lệch hoặc cần hạn chế "
                        "ảnh hưởng của giá trị cực đoan"
                    )

            result[col] = series.fillna(fill)

            add(
                col,
                strategy,
                n_missing,
                round(float(fill), 4),
                reason,
            )
            continue

        # 5. Biến phân loại và văn bản.
        if isinstance(series.dtype, pd.CategoricalDtype):
            series = series.astype(object)

        # Văn bản tự do không điền mode vì có thể tạo nội dung sai.
        if is_free_text_col(col):
            fill = "Unknown"
            result[col] = series.fillna(fill)

            add(
                col,
                "constant",
                n_missing,
                fill,
                "Văn bản tự do/tên riêng; dùng Unknown",
            )
            continue

        valid_count = series.nunique(dropna=True)
        modes = series.mode(dropna=True)

        if valid_count == 0:
            fill = "Unknown"
            strategy = "constant"
            reason = "Toàn bộ giá trị thiếu"

        elif valid_count <= categorical_max and not modes.empty:
            fill = modes.iloc[0]
            strategy = "mode"
            reason = (
                f"Biến phân loại có {valid_count} nhóm; "
                "điền mode"
            )

        else:
            fill = "Unknown"
            strategy = "constant"
            reason = (
                f"Có {valid_count} nhóm hoặc quá nhiều nhóm; "
                "dùng Unknown"
            )

        result[col] = series.fillna(fill)

        add(
            col,
            strategy,
            n_missing,
            fill,
            reason,
        )

    log_df = pd.DataFrame(
        log,
        columns=[
            "column",
            "dtype",
            "missing_count",
            "strategy",
            "fill_value",
            "reason",
        ],
    )

    return result, log_df


def clean_data(
    df: pd.DataFrame,
    return_log: bool = False,
):
    """Pipeline đầy đủ: chuẩn hóa -> xóa trùng -> imputation."""
    prepared = prepare_data(df)
    cleaned, log = impute_missing(prepared)

    if return_log:
        return cleaned, log

    return cleaned
