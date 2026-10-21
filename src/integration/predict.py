
from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd

from src.regression.train_regression import build_features



# CAU HINH DUONG DAN


ROOT = Path(__file__).resolve().parents[2]
MODEL_DIR = ROOT / "models"



# HAM HO TRO


def load_json(path):
    file_path = ROOT / path

    if not file_path.exists():
        raise FileNotFoundError(
            f"Khong tim thay file JSON: {file_path}"
        )

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_model(path):
    model_path = ROOT / path

    if not model_path.exists():
        raise FileNotFoundError(
            f"Khong tim thay model: {model_path}"
        )

    return joblib.load(model_path)


def to_dataframe(data):
    if isinstance(data, pd.DataFrame):
        return data.copy()

    if isinstance(data, pd.Series):
        return data.to_frame().T

    if isinstance(data, dict):
        return pd.DataFrame([data])

    raise TypeError(
        "Du lieu phai la DataFrame, Series hoac dict"
    )



# MEMBER 4 - CLASSIFICATION
# DU DOAN THE LOAI SACH


def predict_classification(data):
    df = to_dataframe(data)

    meta = load_json(
        "models/classification/model_metadata.json"
    )

    model = load_model(
        "models/classification/best_model.joblib"
    )

    features = meta["input_features"]

    missing = [
        col for col in features
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Classification thieu cot: {missing}"
        )

    X = df[features].copy()

    for col in meta["numeric_features"]:
        X[col] = pd.to_numeric(
            X[col],
            errors="coerce"
        )

    for col in meta["categorical_features"]:
        X[col] = (
            X[col]
            .fillna("Unknown")
            .astype(str)
        )

    predictions = model.predict(X)

    return predictions



# MEMBER 3 - REGRESSION
# DU DOAN GIA SACH (GBP)


def predict_regression(data):
    df = to_dataframe(data)

    meta = load_json(
        "models/regression/regression_meta.json"
    )

    model = load_model(
        "models/regression/best_regression_model.joblib"
    )

    top_publishers = meta["top_publishers"]

    # Su dung ham tao feature cua Member 3
    X = build_features(
        df,
        top_publishers=top_publishers
    )

    required = meta["num_cols"] + meta["cat_cols"]

    # Kiem tra cot Cluster_Label neu model can
    if "Cluster_Label" in meta["cat_cols"]:
        if "Cluster_Label" not in X.columns:
            raise ValueError(
                "Regression can cot Cluster_Label tu Member 2"
            )

    missing = [
        col for col in required
        if col not in X.columns
    ]

    if missing:
        raise ValueError(
            f"Regression thieu cot: {missing}"
        )

    X = X[required].copy()

    for col in meta["cat_cols"]:
        X[col] = (
            X[col]
            .fillna("Unknown")
            .astype(str)
        )

    for col in meta["num_cols"]:
        X[col] = pd.to_numeric(
            X[col],
            errors="coerce"
        )

    predictions = model.predict(X)

    # Khong cho gia du doan am
    predictions = np.maximum(predictions, 0)

    return predictions



# MEMBER 2 - KMEANS
# PHAN CUM SACH


def prepare_clustering_features(data):
    df = to_dataframe(data)

    # Lay cau hinh feature tu Member 1
    schema = load_json(
        "models/pca/feature_schema.json"
    )

    features = schema["features"]
    log_cols = schema["log1p_features"]

    missing = [
        col for col in features
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"KMeans thieu cot: {missing}"
        )

    # Lay dung 12 feature theo thu tu khi train
    X = df[features].copy()

    # Chuyen sang du lieu so
    X = X.apply(
        pd.to_numeric,
        errors="coerce"
    )

    # Gia tri am khong hop le
    X[X < 0] = np.nan

    # Xu ly log1p giong Member 1
    X[log_cols] = np.log1p(
        X[log_cols]
    )

    # Load bo tien xu ly
    preprocessing = load_model(
        "models/pca/preprocessing.joblib"
    )

    # Chuan hoa du lieu
    X_processed = preprocessing.transform(X)

    return X_processed


def predict_clustering(data, use_pca=False):
    # Tien xu ly 12 feature
    X_processed = prepare_clustering_features(data)

    if use_pca:
        # Su dung PCA cua Member 1
        pca = load_model(
            "models/pca/pca_model.joblib"
        )

        X_processed = pca.transform(
            X_processed
        )

        model_path = (
            "models/clustering/kmeans_pca.joblib"
        )

    else:
        # KMeans tren 12 feature da tien xu ly
        model_path = (
            "models/clustering/kmeans_original.joblib"
        )

    model = load_model(model_path)

    # Kiem tra so feature
    expected_features = model.n_features_in_

    actual_features = X_processed.shape[1]

    if actual_features != expected_features:
        raise ValueError(
            "So features khong khop voi KMeans: "
            f"{actual_features} != {expected_features}"
        )

    predictions = model.predict(X_processed)

    return predictions



# MEMBER 5 - INTEGRATION
# TICH HOP 3 MODEL


def predict_all(
    data,
    include_clustering=True,
    use_pca=False
):
    df = to_dataframe(data)

    results = pd.DataFrame(index=df.index)

    # Classification
    results["predicted_category"] = (
        predict_classification(df)
    )

    # Regression
    results["predicted_price_gbp"] = (
        predict_regression(df)
    )

    # KMeans
    if include_clustering:
        results["cluster"] = predict_clustering(
            df,
            use_pca=use_pca
        )

    return results



# CHAY THU HE THONG


if __name__ == "__main__":

    data_path = (
        ROOT / "data" / "cleaned" / "cleaned_data.csv"
    )

    if not data_path.exists():
        print(
            "Khong tim thay cleaned_data.csv"
        )

    else:
        # Lay 5 dong de kiem tra
        df = pd.read_csv(
            data_path,
            nrows=5
        )

        print("=" * 60)
        print("KIEM TRA HE THONG TICH HOP AI")
        print("=" * 60)

        
        # CLASSIFICATION
        

        print("\n=== CLASSIFICATION ===")

        try:
            classification_result = (
                predict_classification(df)
            )

            print(classification_result)

        except Exception as e:
            print(
                "Loi Classification:", e
            )

        
        # REGRESSION
        

        print("\n=== REGRESSION ===")

        try:
            regression_result = (
                predict_regression(df)
            )

            print(regression_result)

        except Exception as e:
            print(
                "Loi Regression:", e
            )

        
        # KMEANS ORIGINAL
        

        print("\n=== KMEANS ORIGINAL ===")

        try:
            clustering_result = (
                predict_clustering(
                    df,
                    use_pca=False
                )
            )

            print(clustering_result)

        except Exception as e:
            print(
                "Loi KMeans:", e
            )

        
        # INTEGRATION
        

        print("\n=== INTEGRATION 3 MODELS ===")

        try:
            results = predict_all(
                df,
                include_clustering=True,
                use_pca=False
            )

            print(
                results.to_string(index=False)
            )

            print(
                "\nTich hop 3 model thanh cong!"
            )

        except Exception as e:
            print(
                "Loi Integration:", e
            )

        print("\n" + "=" * 60)
        print("KET THUC KIEM TRA")
        print("=" * 60)
