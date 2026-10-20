"""
Member 3 - Regression: du doan gia sach (gbpprice, don vi GBP).

Chay (tu thu muc goc project):
    python src/regression/train_regression.py
    python src/regression/train_regression.py --data data/stage2/clustering/data_with_cluster.csv

Dau ra:
    models/regression/best_regression_model.joblib   (pipeline gom preprocessing + model)
    models/regression/regression_meta.json           (danh sach feature, metrics, ten model)
    visualization/stage2/regression/*.png
    reports/stage2/regression_analysis.md
"""
import argparse
import json
import re
from pathlib import Path

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeRegressor

RANDOM_STATE = 42
TARGET = "gbpprice"
# Cac dong co gbpprice > nguong nay la sach tieng Viet (gia VND bi tron vao cot gbpprice)
MAX_GBP = 1000

NUM_COLS = ["no_of_pages", "height", "width", "spine", "weight", "salesRank",
            "discount", "pub_year", "has_subtitle", "has_edition",
            "short_blurb_len", "long_blurb_len", "has_review"]
CAT_COLS = ["type", "category", "language", "published_country", "publisher_top"]
CLUSTER_COL = "Cluster_Label"  # chi dung neu file dau vao co cot nay (M2 ban giao)

ROOT = Path(__file__).resolve().parents[2]
MODEL_DIR = ROOT / "models" / "regression"
VIS_DIR = ROOT / "visualization" / "stage2" / "regression"
REPORT_DIR = ROOT / "reports" / "stage2"


# ------------------------------------------------------------------ features
def parse_pages(s):
    """'xv, 447' -> 447 ; '456' -> 456 ; khong co so -> NaN"""
    m = re.findall(r"\d+", str(s))
    return float(m[-1]) if m else np.nan


def build_features(df: pd.DataFrame, top_publishers=None):
    """Tao feature tu dataframe tho. Dung chung cho train va predict (M5)."""
    out = pd.DataFrame(index=df.index)
    out["no_of_pages"] = df["no_of_pages"].map(parse_pages)
    for c in ["height", "width", "spine", "weight", "salesRank", "discount"]:
        out[c] = pd.to_numeric(df[c], errors="coerce")
    out["pub_year"] = pd.to_datetime(df["publication_date"], errors="coerce").dt.year
    out["has_subtitle"] = (df["subtitle"].fillna("Unknown") != "Unknown").astype(int)
    out["has_edition"] = (df["edition"].fillna("Unknown") != "Unknown").astype(int)
    out["short_blurb_len"] = df["short_blurb"].fillna("").str.len()
    out["long_blurb_len"] = df["long_blurb"].fillna("").str.len()
    out["has_review"] = (df["blurbReview"].fillna("Unknown") != "Unknown").astype(int)
    for c in ["type", "category", "language", "published_country"]:
        out[c] = df[c].fillna("Unknown").astype(str)
    out["publisher_top"] = df["publisher"].fillna("Unknown").astype(str)
    if top_publishers is not None:  # gom nha xuat ban hiem thanh 'Other'
        out["publisher_top"] = out["publisher_top"].where(
            out["publisher_top"].isin(top_publishers), "Other")
    if CLUSTER_COL in df.columns:
        out[CLUSTER_COL] = df[CLUSTER_COL].astype(str)
    return out


def make_preprocessor(cat_cols, num_cols, scale):
    num = [("imputer", SimpleImputer(strategy="median"))]
    if scale:
        num.append(("scaler", StandardScaler()))
    return ColumnTransformer([
        ("num", Pipeline(num), num_cols),
        ("cat", OneHotEncoder(handle_unknown="ignore", min_frequency=5), cat_cols),
    ])


# ------------------------------------------------------------------ main
def main(args):
    for d in (MODEL_DIR, VIS_DIR, REPORT_DIR):
        d.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(args.data)
    n_raw = len(df)
    df = df[df[TARGET] <= MAX_GBP].reset_index(drop=True)
    print(f"Doc {n_raw} dong, giu {len(df)} dong sach UK (loai {n_raw-len(df)} dong gia VND)")

    top_publishers = df["publisher"].value_counts().head(50).index.tolist()
    X = build_features(df, top_publishers)
    y = df[TARGET].astype(float)

    num_cols, cat_cols = list(NUM_COLS), list(CAT_COLS)
    if CLUSTER_COL in X.columns:
        cat_cols.append(CLUSTER_COL)
        print("Dung Cluster_Label lam feature")

    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=RANDOM_STATE)

    def wrap(model, scale):
        pipe = Pipeline([("prep", make_preprocessor(cat_cols, num_cols, scale)), ("model", model)])
        # Gia sach lech phai manh -> huan luyen tren log1p(gia), du doan tra ve GBP
        return TransformedTargetRegressor(regressor=pipe, func=np.log1p, inverse_func=np.expm1)

    models = {
        "LinearRegression": wrap(LinearRegression(), scale=True),
        "DecisionTreeRegressor": wrap(
            DecisionTreeRegressor(max_depth=8, min_samples_leaf=20, random_state=RANDOM_STATE),
            scale=False),
    }

    rows, preds = [], {}
    for name, m in models.items():
        m.fit(X_tr, y_tr)
        p = np.clip(m.predict(X_te), 0, None)
        preds[name] = p
        mse = mean_squared_error(y_te, p)
        rows.append({
            "Model": name,
            "MSE": mse,
            "RMSE": np.sqrt(mse),
            "MAE": mean_absolute_error(y_te, p),
            "R2": r2_score(y_te, p),
            "R2_log": r2_score(np.log1p(y_te), np.log1p(p)),
            "R2_train": r2_score(y_tr, np.clip(m.predict(X_tr), 0, None)),
        })
    res = pd.DataFrame(rows).set_index("Model")
    print(res.round(4))

    # baseline: luon du doan trung binh (de biet model co hoc duoc gi khong)
    base = np.full(len(y_te), y_tr.mean())
    base_rmse = float(np.sqrt(mean_squared_error(y_te, base)))
    print(f"Baseline (du doan trung binh) RMSE = {base_rmse:.3f}")

    best_name = res["RMSE"].idxmin()
    best = models[best_name]
    print("Model tot nhat:", best_name)

    # ---------------------------------------------------------- plots
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax, (name, p) in zip(axes, preds.items()):
        ax.scatter(y_te, p, s=8, alpha=0.4)
        lim = [0, float(np.percentile(y_te, 99))]
        ax.plot(lim, lim, "r--", lw=1)
        ax.set(xlim=lim, ylim=lim, xlabel="Actual (GBP)", ylabel="Predicted (GBP)",
               title=f"{name}\nR2={res.loc[name,'R2']:.3f}, RMSE={res.loc[name,'RMSE']:.2f}")
    plt.tight_layout(); plt.savefig(VIS_DIR / "actual_vs_predicted.png", dpi=150); plt.close()

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax, (name, p) in zip(axes, preds.items()):
        resid = y_te.values - p
        ax.scatter(p, resid, s=8, alpha=0.4)
        ax.axhline(0, color="r", ls="--", lw=1)
        ax.set(xlabel="Predicted (GBP)", ylabel="Residual (Actual - Predicted)",
               title=f"Residual plot - {name}",
               xlim=(0, float(np.percentile(p, 99))),
               ylim=(float(np.percentile(resid, 1)), float(np.percentile(resid, 99))))
    plt.tight_layout(); plt.savefig(VIS_DIR / "residual_plot.png", dpi=150); plt.close()

    res[["RMSE", "MAE"]].plot(kind="bar", figsize=(6, 4), rot=0, title="So sanh loi tren tap test (GBP)")
    plt.tight_layout(); plt.savefig(VIS_DIR / "model_comparison.png", dpi=150); plt.close()

    # feature importance cua Decision Tree
    dt = models["DecisionTreeRegressor"].regressor_
    names = dt.named_steps["prep"].get_feature_names_out()
    imp = pd.Series(dt.named_steps["model"].feature_importances_, index=names).sort_values()
    imp.tail(15).plot(kind="barh", figsize=(7, 5), title="Top 15 feature importance (Decision Tree)")
    plt.tight_layout(); plt.savefig(VIS_DIR / "feature_importance.png", dpi=150); plt.close()
    top_feats = imp.sort_values(ascending=False).head(5)

    # ---------------------------------------------------------- save
    joblib.dump(best, MODEL_DIR / "best_regression_model.joblib")
    meta = {
        "best_model": best_name,
        "target": TARGET, "target_unit": "GBP",
        "num_cols": num_cols, "cat_cols": cat_cols,
        "top_publishers": top_publishers,
        "metrics": res.round(4).to_dict(orient="index"),
        "baseline_rmse": base_rmse,
        "n_train": len(X_tr), "n_test": len(X_te),
    }
    (MODEL_DIR / "regression_meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))

    # ---------------------------------------------------------- report
    resid_best = y_te.values - preds[best_name]
    over_rate = float((resid_best > 0).mean())
    md = f"""# Regression Analysis - Du doan gia sach (gbpprice)

## 1. Thiet lap
- Target: `{TARGET}` (GBP, lien tuc). Chi dung {len(df)} dong sach UK; {n_raw-len(df)} dong sach tieng Viet co gia VND bi tron vao cung cot nen bi loai.
- Chia train/test 80/20 (`random_state={RANDOM_STATE}`): {len(X_tr)} / {len(X_te)} dong.
- Gia lech phai manh nen model hoc tren `log1p(gia)` va chuyen nguoc ve GBP khi du doan.
- Feature so: {', '.join(num_cols)}.
- Feature phan loai (One-Hot): {', '.join(cat_cols)}.
- Da loai: isbn, link, name, author, cac cot rat dai (chi lay do dai), cac cot tieng Viet/VND (hang so cho sach UK), `isSecondHand` (hang so).

## 2. Ket qua tren tap test
{res.round(4).to_markdown()}

Baseline (luon du doan gia trung binh): RMSE = {base_rmse:.3f} GBP.

## 3. Model tot nhat
**{best_name}** (RMSE thap nhat).

## 4. Phan tich sai so
- Top feature quan trong (Decision Tree): {', '.join(top_feats.index)}.
- Ti le du doan thap hon thuc te: {over_rate:.1%} (residual > 0).
- Xem `residual_plot.png`: neu residual tang theo gia du doan thi mo hinh sai so co he thong o nhom sach dat (artanddesign, hardback...). 
- Cac feature vat ly (kich thuoc, trong luong) va salesRank gan nhu khong tuong quan truc tiep voi gia, nen R2 bi gioi han.

## 5. Ban giao cho M5
- File: `models/regression/best_regression_model.joblib` (pipeline gom preprocessing + model, goi `.predict(DataFrame)` ra gia GBP).
- Dung `build_features()` trong `src/regression/train_regression.py` de tao DataFrame dau vao tu du lieu tho; chi tiet cot nam trong `regression_meta.json`.
"""
    (REPORT_DIR / "regression_analysis.md").write_text(md, encoding="utf-8")
    print("Da luu model, bieu do va bao cao.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=str(ROOT / "data" / "cleaned_data.csv"))
    main(ap.parse_args())
