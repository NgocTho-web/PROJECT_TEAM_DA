# Member 1 - Stage 2: Giam chieu du lieu bang PCA
# Chay file nay tai thu muc goc cua project: python src/pca/train_pca.py

from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / "data/cleaned/cleaned_data.csv"
DATA_OUT = ROOT / "data/stage2/pca"
MODEL_OUT = ROOT / "models/pca"
CHART_OUT = ROOT / "visualization/stage2/pca"

# Chon cac cot so co the dung cho PCA, khong lay ID va cot chu
features = ["gbpprice", "discount", "height", "width", "spine", "weight",
            "salesRank", "original_price", "discount_price",
            "discount_percentage", "rating", "rating_count"]
log_cols = ["gbpprice", "discount", "salesRank", "original_price",
            "discount_price", "rating_count"]


def prepare(df):
    # Chuyen cac cot ve dang so va xu ly gia tri khong hop le
    x = df[features].apply(pd.to_numeric, errors="coerce").copy()
    for col in features:
        if col != "rating":
            x.loc[x[col] < 0, col] = np.nan
    x.loc[~x["rating"].between(0, 5), "rating"] = np.nan

    # Log1p giup giam anh huong cua cac gia tri qua lon
    for col in log_cols:
        x[col] = np.log1p(x[col])
    return x


def main():
    for folder in [DATA_OUT, MODEL_OUT, CHART_OUT]:
        folder.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(INPUT, low_memory=False)
    x = prepare(df)

    # Dien gia tri thieu bang trung vi, sau do chuan hoa
    preprocessing = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])
    x_scaled = preprocessing.fit_transform(x)

    # Chay PCA de xem moi thanh phan giai thich bao nhieu phuong sai
    pca_all = PCA(svd_solver="full")
    pca_all.fit(x_scaled)
    variance = pca_all.explained_variance_ratio_
    cumulative = np.cumsum(variance)

    # Chon so thanh phan it nhat giu duoc >= 90% phuong sai
    n_components = int(np.searchsorted(cumulative, 0.90) + 1)
    pca = PCA(n_components=n_components, svd_solver="full")
    x_pca = pca.fit_transform(x_scaled)
    pc_names = [f"PC{i+1}" for i in range(n_components)]

    # Luu du lieu sau PCA, giu source_row de ghep lai voi du lieu goc
    pca_df = pd.DataFrame(x_pca, columns=pc_names)
    pca_df.insert(0, "source_row", np.arange(len(df)))
    pca_df.to_csv(DATA_OUT / "pca_features.csv", index=False)
    pd.DataFrame({"source_row": np.arange(len(df)), "isbn": df["isbn"]}).to_csv(
        DATA_OUT / "row_mapping.csv", index=False)

    variance_df = pd.DataFrame({
        "component": np.arange(1, len(variance)+1),
        "explained_variance_ratio": variance,
        "cumulative_explained_variance": cumulative
    })
    variance_df.to_csv(DATA_OUT / "explained_variance.csv", index=False)
    pd.DataFrame(pca.components_.T, index=features, columns=pc_names).to_csv(
        DATA_OUT / "pca_loadings.csv", index_label="feature")

    # Luu model va thong tin cac cot de member 2 dung tiep
    joblib.dump(preprocessing, MODEL_OUT / "preprocessing.joblib")
    joblib.dump(pca, MODEL_OUT / "pca_model.joblib")
    schema = {"features": features, "log1p_features": log_cols,
              "n_components": n_components, "target_variance": 0.90,
              "retained_variance": float(cumulative[n_components-1]),
              "source_rows": len(df),
              "source_file": "data/cleaned/cleaned_data.csv"}
    (MODEL_OUT / "feature_schema.json").write_text(
        json.dumps(schema, indent=2), encoding="utf-8")

    # Bieu do phuong sai tich luy
    plt.figure(figsize=(8, 5))
    plt.plot(variance_df["component"], cumulative, marker="o")
    plt.axhline(0.90, linestyle="--", label="Muc tieu 90%")
    plt.axvline(n_components, linestyle=":", label=f"{n_components} thanh phan")
    plt.xlabel("So thanh phan PCA")
    plt.ylabel("Phuong sai tich luy")
    plt.title("Cumulative Explained Variance")
    plt.legend()
    plt.grid(alpha=0.25)
    plt.tight_layout()
    plt.savefig(CHART_OUT / "cumulative_variance.png", dpi=160)
    plt.close()

    # Bieu do PCA 2D
    plt.figure(figsize=(8, 6))
    plt.scatter(x_pca[:, 0], x_pca[:, 1], s=4, alpha=0.25)
    plt.xlabel("PC1")
    plt.ylabel("PC2")
    plt.title("PCA Scatter Plot 2D")
    plt.tight_layout()
    plt.savefig(CHART_OUT / "pca_scatter_2d.png", dpi=160)
    plt.close()

    print("So dong:", len(df))
    print("So features:", len(features))
    print("So thanh phan PCA:", n_components)
    print("Phuong sai giu lai: {:.2%}".format(cumulative[n_components-1]))


if __name__ == "__main__":
    main()
