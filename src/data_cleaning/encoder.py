import pandas as pd


def encode_features(df: pd.DataFrame) -> pd.DataFrame:
    """Tự động tìm các cột dạng chữ và chuyển đổi sang One-Hot Encoding."""
    categorical_cols = df.select_dtypes(include=["object"]).columns.tolist()

    if categorical_cols:
        df = pd.get_dummies(
            df, columns=categorical_cols, drop_first=True, dtype=int
        )

    return df