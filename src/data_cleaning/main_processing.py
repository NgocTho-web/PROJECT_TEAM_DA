from __future__ import annotations
 
from pathlib import Path
 
import matplotlib
import numpy as np
import pandas as pd
 
matplotlib.use("Agg")
import matplotlib.pyplot as plt
 
try:
    from scipy import stats as sp_stats
except ImportError:  # scipy là tùy chọn: thiếu thì bỏ Shapiro/KDE
    sp_stats = None
 
try:  # chạy trực tiếp bằng py src/data_cleaning/main_processing.py
    from cleaner import (impute_missing, is_free_text_col, is_identifier_col,
                         normalize_missing_tokens, prepare_data)
except ImportError:  # chạy dưới dạng module
    from src.data_cleaning.cleaner import (impute_missing, is_free_text_col, is_identifier_col,
                                           normalize_missing_tokens, prepare_data)
 
ROOT_DIR = Path(__file__).resolve().parents[2]
RETRIEVED_DIR = ROOT_DIR / "data" / "retrieved"
OUTPUT_DIR = ROOT_DIR / "data" / "cleaned"
EDA_DIR = ROOT_DIR / "data" / "eda_reports"
 
# Ưu tiên SQLite; nếu chưa có thì dùng file đã retrieve từ Qdrant (do Member 3 xuất).
INPUT_CANDIDATES = [
    RETRIEVED_DIR / "sqlite_retrieved.csv",
    RETRIEVED_DIR / "qdrant_retrieved.csv",
]
 
MAX_PLOT_COLUMNS = 12
MAX_FREQ_CATEGORIES = 50
CSV_KW = {"index": False, "encoding": "utf-8-sig"}
 
 
# ---------------------------------------------------------------- helpers
def _safe_name(col: object) -> str:
    return "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in str(col))[:80]
 
 
def _pct_change(before: float, after: float) -> float:
    if pd.isna(before) or pd.isna(after) or before == 0:
        return np.nan
    return round((after - before) / abs(before) * 100, 2)
 
 
def _md_table(df: pd.DataFrame, max_rows: int = 60) -> str:
    if df.empty:
        return "_(không có)_\n"
    df = df.head(max_rows).copy()
    cells = df.map(lambda v: f"{v:.4g}" if isinstance(v, float) else str(v))
    lines = ["| " + " | ".join(map(str, df.columns)) + " |",
             "|" + "|".join("---" for _ in df.columns) + "|"]
    lines += ["| " + " | ".join(row) + " |" for row in cells.to_numpy()]
    return "\n".join(lines) + "\n"
 
 
def _analysis_numeric_cols(df: pd.DataFrame) -> list[str]:
    """Cột số có ý nghĩa thống kê: bỏ bool và cột ID."""
    return [c for c in df.select_dtypes(include=["number"]).columns
            if not pd.api.types.is_bool_dtype(df[c]) and not is_identifier_col(c)]
 
 
def _categorical_cols(df: pd.DataFrame, max_categories: int) -> list[str]:
    cols = []
    for c in df.select_dtypes(include=["object", "string", "category", "bool"]).columns:
        if is_identifier_col(c) or is_free_text_col(c):
            continue
        if df[c].nunique(dropna=True) <= max_categories:
            cols.append(c)
    return cols
 
 
# ---------------------------------------------------------------- missing
def _missing_before_report(raw: pd.DataFrame, normalized: pd.DataFrame) -> pd.DataFrame:
    raw_nan = raw.isna().sum()
    total = normalized.isna().sum()
    n = max(len(raw), 1)
    return pd.DataFrame({
        "column": raw.columns,
        "raw_nan_count": raw_nan.values,
        "invalid_token_count": (total - raw_nan).values,
        "missing_count": total.values,
        "missing_percentage": (total / n * 100).round(2).values,
    })
 
 
def _missing_after_report(df: pd.DataFrame) -> pd.DataFrame:
    count = df.isna().sum()
    return pd.DataFrame({"column": df.columns, "missing_count": count.values,
                         "missing_percentage": (count / max(len(df), 1) * 100).round(2).values})
 
 
def _save_missingno(df: pd.DataFrame, out_dir: Path) -> None:
    try:
        import missingno as msno
    except ImportError:
        print("   (bỏ qua missingno: chưa cài, dùng `pip install missingno`)")
        return
    if df.isna().sum().sum() == 0:
        return
    try:
        ax = msno.matrix(df, sparkline=False, fontsize=8)
        ax.get_figure().savefig(out_dir / "missingno_matrix.png", dpi=120, bbox_inches="tight")
        plt.close("all")
        if (df.isna().sum() > 0).sum() >= 2:
            ax = msno.heatmap(df, fontsize=8)
            ax.get_figure().savefig(out_dir / "missingno_heatmap.png", dpi=120, bbox_inches="tight")
            plt.close("all")
    except Exception as exc:  # noqa: BLE001 - biểu đồ phụ không được làm hỏng pipeline
        plt.close("all")
        print(f"   (missingno lỗi: {exc})")
 
 
# ---------------------------------------------------------------- univariate
def _distribution_label(skew: float, kurt: float, shapiro_p: float) -> str:
    if pd.isna(skew):
        return "không đủ dữ liệu"
    if abs(skew) < 0.5:
        label = "gần đối xứng"
    else:
        strength = "mạnh" if abs(skew) > 1 else "vừa"
        label = f"lệch {'phải' if skew > 0 else 'trái'} ({strength})"
    if pd.notna(kurt) and kurt > 1:
        label += ", đuôi dày"
    elif pd.notna(kurt) and kurt < -1:
        label += ", đuôi mỏng"
    if pd.notna(shapiro_p):
        label += "; chuẩn" if shapiro_p >= 0.05 else "; không chuẩn"
        label += f" (Shapiro p={shapiro_p:.3g})"
    return label
 
 
def _numeric_eda(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    cols = _analysis_numeric_cols(df)
    stat_rows, out_rows = [], []
    for col in cols:
        v = df[col].replace([np.inf, -np.inf], np.nan).dropna()
        if v.empty:
            continue
        skew, kurt = v.skew(), v.kurt()
        p = np.nan
        if sp_stats is not None and 3 <= len(v) and v.nunique() > 1:
            sample = v.sample(5000, random_state=42) if len(v) > 5000 else v
            p = float(sp_stats.shapiro(sample).pvalue)
        stat_rows.append({"column": col, "count": int(v.count()), "mean": v.mean(), "median": v.median(),
                          "std": v.std(), "skewness": skew, "kurtosis": kurt, "shapiro_p": p,
                          "distribution": _distribution_label(skew, kurt, p)})
 
        q1, q3 = v.quantile(0.25), v.quantile(0.75)
        iqr = q3 - q1
        lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        iqr_mask = (v < lower) | (v > upper)
        std = v.std(ddof=0)
        z_count = int((((v - v.mean()) / std).abs() > 3).sum()) if std > 0 else 0
        pct = round(float(iqr_mask.mean() * 100), 2)
        if iqr_mask.sum() == 0:
            decision = "Không có outlier"
        elif pct < 5:
            decision = "Tỷ lệ thấp: giữ lại, kiểm tra thủ công giá trị cực đoan"
        else:
            decision = "Tỷ lệ cao: phân phối lệch/đuôi dày, cân nhắc biến đổi log hoặc winsorize"
        out_rows.append({"column": col, "Q1": q1, "Q3": q3, "IQR": iqr, "lower_bound": lower,
                         "upper_bound": upper, "iqr_outlier_count": int(iqr_mask.sum()),
                         "iqr_outlier_pct": pct, "zscore_outlier_count": z_count, "decision": decision})
    stats_cols = ["column", "count", "mean", "median", "std", "skewness", "kurtosis", "shapiro_p", "distribution"]
    out_cols = ["column", "Q1", "Q3", "IQR", "lower_bound", "upper_bound", "iqr_outlier_count",
                "iqr_outlier_pct", "zscore_outlier_count", "decision"]
    return pd.DataFrame(stat_rows, columns=stats_cols), pd.DataFrame(out_rows, columns=out_cols)
 
 
def _categorical_frequency(df: pd.DataFrame, max_categories: int = MAX_FREQ_CATEGORIES) -> pd.DataFrame:
    frames = []
    for col in _categorical_cols(df, max_categories):
        counts = df[col].fillna("NaN").astype(str).value_counts(dropna=False)
        temp = counts.rename_axis("category").reset_index(name="frequency")
        temp.insert(0, "column", col)
        temp["percentage"] = (temp["frequency"] / max(len(df), 1) * 100).round(2)
        frames.append(temp)
    if not frames:
        return pd.DataFrame(columns=["column", "category", "frequency", "percentage"])
    return pd.concat(frames, ignore_index=True)
 
 
def _boxplot(ax, values) -> None:
    try:
        ax.boxplot(values, orientation="horizontal")  # matplotlib >= 3.10
    except TypeError:
        ax.boxplot(values, vert=False)
 
 
def _save_plots(df: pd.DataFrame, out_dir: Path, max_columns: int = MAX_PLOT_COLUMNS) -> list[str]:
    cols = [c for c in _analysis_numeric_cols(df) if df[c].nunique(dropna=True) > 1][:max_columns]
    if not cols:
        print("   Không có cột số phù hợp để vẽ histogram/boxplot.")
    for i, col in enumerate(cols, 1):
        values = df[col].replace([np.inf, -np.inf], np.nan).dropna()
        name = f"{i:02d}_{_safe_name(col)}"  # prefix số thứ tự để tên file không bao giờ trùng
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.hist(values, bins="auto", edgecolor="black")
        ax.set_title(f"Distribution of {col}")
        ax.set_xlabel(str(col))
        ax.set_ylabel("Frequency")
        fig.tight_layout()
        fig.savefig(out_dir / f"hist_{name}.png", dpi=120)
        plt.close(fig)
 
        fig, ax = plt.subplots(figsize=(7, 4))
        _boxplot(ax, values)
        ax.set_title(f"Box Plot of {col}")
        ax.set_xlabel(str(col))
        fig.tight_layout()
        fig.savefig(out_dir / f"boxplot_{name}.png", dpi=120)
        plt.close(fig)
    return cols
 
 
# ---------------------------------------------------------------- before / after
def _numeric_before_after(before: pd.DataFrame, after: pd.DataFrame) -> pd.DataFrame:
    """So sánh trên CÙNG tập dòng (đã dedupe, trước vs sau điền thiếu)."""
    rows = []
    for col in _analysis_numeric_cols(after):
        if col not in before.columns:
            continue
        b = pd.to_numeric(before[col], errors="coerce").replace([np.inf, -np.inf], np.nan)
        a = pd.to_numeric(after[col], errors="coerce")
        row = {"column": col, "before_count": int(b.count()), "after_count": int(a.count()),
               "before_mean": b.mean(), "after_mean": a.mean(),
               "before_median": b.median(), "after_median": a.median(),
               "before_std": b.std(), "after_std": a.std(),
               "before_skew": b.skew(), "after_skew": a.skew()}
        row["mean_change_pct"] = _pct_change(row["before_mean"], row["after_mean"])
        row["median_change_pct"] = _pct_change(row["before_median"], row["after_median"])
        row["std_change_pct"] = _pct_change(row["before_std"], row["after_std"])
        big = (abs(row["mean_change_pct"]) > 10 if pd.notna(row["mean_change_pct"]) else False) or \
              (abs(row["std_change_pct"]) > 20 if pd.notna(row["std_change_pct"]) else False)
        row["assessment"] = "CẦN KIỂM TRA: phân phối thay đổi đáng kể" if big else "OK"
        rows.append(row)
    return pd.DataFrame(rows)
 
 
def _categorical_before_after(before: pd.DataFrame, after: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in _categorical_cols(after, 30):
        if col not in before.columns:
            continue
        n_b, n_a = max(len(before), 1), max(len(after), 1)
        vc_b = before[col].value_counts(dropna=True)
        vc_a = after[col].value_counts(dropna=True)
        if vc_a.empty:
            continue
        top_a = vc_a.index[0]
        share_b = (vc_b.get(top_a, 0) / n_b) * 100
        share_a = vc_a.iloc[0] / n_a * 100
        rows.append({"column": col, "top_category_after": top_a, "share_before_pct": round(share_b, 2),
                     "share_after_pct": round(share_a, 2), "change_pp": round(share_a - share_b, 2),
                     "assessment": "CẦN KIỂM TRA: mode-impute làm phình nhóm đầu" if share_a - share_b > 10 else "OK"})
    return pd.DataFrame(rows, columns=["column", "top_category_after", "share_before_pct",
                                       "share_after_pct", "change_pp", "assessment"])
 
 
def _save_comparison_plots(before: pd.DataFrame, after: pd.DataFrame, comp: pd.DataFrame,
                           out_dir: Path, max_columns: int = MAX_PLOT_COLUMNS) -> None:
    changed = comp[comp["before_count"] != comp["after_count"]]["column"].tolist()[:max_columns]
    for i, col in enumerate(changed, 1):
        b = pd.to_numeric(before[col], errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
        a = pd.to_numeric(after[col], errors="coerce").dropna()
        if b.empty or a.empty or a.nunique() < 2:
            continue
        fig, ax = plt.subplots(figsize=(7, 4))
        bins = np.histogram_bin_edges(a, bins="auto")
        ax.hist(b, bins=bins, density=True, alpha=0.45, label="Before imputation")
        ax.hist(a, bins=bins, density=True, alpha=0.45, label="After imputation")
        if sp_stats is not None and b.nunique() > 1:
            xs = np.linspace(a.min(), a.max(), 200)
            ax.plot(xs, sp_stats.gaussian_kde(b)(xs), label="KDE before")
            ax.plot(xs, sp_stats.gaussian_kde(a)(xs), linestyle="--", label="KDE after")
        ax.set_title(f"Before vs After Imputation: {col}")
        ax.set_xlabel(str(col))
        ax.set_ylabel("Density")
        ax.legend()
        fig.tight_layout()
        fig.savefig(out_dir / f"compare_{i:02d}_{_safe_name(col)}.png", dpi=120)
        plt.close(fig)
 
 
# ---------------------------------------------------------------- report
def _write_report(path: Path, *, input_path: Path, n_raw: int, n_prepared: int, n_cols: int,
                  missing_before: pd.DataFrame, missing_after: pd.DataFrame, log: pd.DataFrame,
                  stats: pd.DataFrame, outliers: pd.DataFrame, num_cmp: pd.DataFrame,
                  cat_cmp: pd.DataFrame) -> None:
    has_missing = missing_before[missing_before["missing_count"] > 0]
    flagged = pd.concat([num_cmp[num_cmp["assessment"] != "OK"][["column", "assessment"]] if not num_cmp.empty else None,
                         cat_cmp[cat_cmp["assessment"] != "OK"][["column", "assessment"]] if not cat_cmp.empty else None])
    parts = [
        "# Imputation & Univariate EDA Report\n",
        f"- Nguồn dữ liệu: `{input_path}`",
        f"- Kích thước ban đầu: {n_raw} dòng x {n_cols} cột",
        f"- Số dòng sau chuẩn hóa và xóa trùng: {n_prepared} (đã xóa {n_raw - n_prepared} dòng trùng)",
        f"- Tổng giá trị thiếu trước xử lý: {int(missing_before['missing_count'].sum())}",
        f"- Tổng giá trị thiếu sau xử lý: {int(missing_after['missing_count'].sum())}\n",
        "## 1. Missing value trước imputation (gồm cả token lỗi như unknown, n/a, rỗng)\n",
        _md_table(has_missing),
        "## 2. Chiến lược imputation và lý do\n",
        _md_table(log),
        "## 3. So sánh phân phối trước/sau (cùng tập dòng)\n",
        "### Biến số\n", _md_table(num_cmp[["column", "before_count", "after_count", "mean_change_pct",
                                              "median_change_pct", "std_change_pct", "assessment"]]
                                  if not num_cmp.empty else num_cmp),
        "### Biến phân loại\n", _md_table(cat_cmp),
        "**Cột cần kiểm tra:** " + (", ".join(f"`{c}`" for c in flagged["column"]) if len(flagged) else "không có") + "\n",
        "## 4. Thống kê mô tả và kết luận phân phối\n",
        _md_table(stats[["column", "count", "mean", "median", "std", "skewness", "kurtosis", "distribution"]]
                  if not stats.empty else stats),
        "## 5. Outlier (IQR và Z-score > 3)\n",
        _md_table(outliers[["column", "iqr_outlier_count", "iqr_outlier_pct", "zscore_outlier_count", "decision"]]
                  if not outliers.empty else outliers),
    ]
    path.write_text("\n".join(parts), encoding="utf-8")
 
 
# ---------------------------------------------------------------- main
def main() -> None:
    print("=" * 68)
    print("MEMBER 4: ADVANCED DATA CLEANING + UNIVARIATE EDA")
    print("=" * 68)
 
    input_path = next((p for p in INPUT_CANDIDATES if p.exists()), None)
    if input_path is None:
        expected = "\n".join(str(p) for p in INPUT_CANDIDATES)
        raise FileNotFoundError(
            "Không tìm thấy file đã retrieve từ Member 3. Hãy chạy retrieve_data.py trước.\n"
            f"Đã kiểm tra:\n{expected}")
 
    # keep_default_na=False: giữ nguyên "NA"/"null"/"n/a" để đếm đúng token lỗi ở bước assessment.
    df = pd.read_csv(input_path, low_memory=False, keep_default_na=False, na_values=[""])
    if df.empty:
        raise ValueError(f"Dataset đầu vào rỗng: {input_path}")
    if not df.columns.is_unique:
        raise ValueError("Dataset có tên cột trùng; cần xử lý trước khi tiếp tục.")
 
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    EDA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Nguồn dữ liệu: {input_path}")
    print(f"Kích thước ban đầu: {df.shape[0]} dòng x {df.shape[1]} cột")
 
    print("\n1. Missing Value Assessment (trước imputation)...")
    normalized = normalize_missing_tokens(df)
    missing_before = _missing_before_report(df, normalized)
    missing_before.to_csv(EDA_DIR / "missing_values_before.csv", **CSV_KW)
    _save_missingno(normalized, EDA_DIR)
 
    print("2. Làm sạch và điền dữ liệu thiếu...")
    prepared = prepare_data(df)  # đã chuẩn hóa + bỏ trùng, CHƯA điền thiếu
    cleaned, log = impute_missing(prepared)
    missing_after = _missing_after_report(cleaned)
    missing_after.to_csv(EDA_DIR / "missing_values_after.csv", **CSV_KW)
    log.to_csv(EDA_DIR / "imputation_log.csv", **CSV_KW)
    cleaned_path = OUTPUT_DIR / "cleaned_data.csv"
    cleaned.to_csv(cleaned_path, **CSV_KW)
 
    print(f"   Số dòng sau xóa trùng: {len(cleaned)} (đã xóa {len(df) - len(cleaned)})")
    print(f"   Tổng giá trị thiếu trước xử lý: {int(normalized.isna().sum().sum())}")
    print(f"   Tổng giá trị thiếu sau xử lý: {int(cleaned.isna().sum().sum())}")
 
    print("3. So sánh phân phối trước/sau imputation...")
    num_cmp = _numeric_before_after(prepared, cleaned)
    cat_cmp = _categorical_before_after(prepared, cleaned)
    num_cmp.to_csv(EDA_DIR / "before_after_imputation.csv", **CSV_KW)
    cat_cmp.to_csv(EDA_DIR / "before_after_categorical.csv", **CSV_KW)
    _save_comparison_plots(prepared, cleaned, num_cmp, EDA_DIR)
 
    print("4. Thống kê biến số, kết luận phân phối, outlier (IQR + Z-score)...")
    stats, outliers = _numeric_eda(cleaned)
    stats.to_csv(EDA_DIR / "numerical_univariate_stats.csv", **CSV_KW)
    outliers.to_csv(EDA_DIR / "outlier_iqr_summary.csv", **CSV_KW)
 
    print("5. Tần suất và tỷ lệ biến phân loại...")
    _categorical_frequency(cleaned).to_csv(EDA_DIR / "categorical_frequency.csv", **CSV_KW)
 
    print(f"6. Vẽ histogram và box plot (tối đa {MAX_PLOT_COLUMNS} biến số)...")
    _save_plots(cleaned, EDA_DIR)
 
    print("7. Viết imputation_report.md...")
    _write_report(EDA_DIR / "imputation_report.md", input_path=input_path, n_raw=len(df),
                  n_prepared=len(prepared), n_cols=df.shape[1], missing_before=missing_before,
                  missing_after=missing_after, log=log, stats=stats, outliers=outliers,
                  num_cmp=num_cmp, cat_cmp=cat_cmp)
 
    print("\nKẾT QUẢ ĐÃ LƯU")
    print(f"- Dataset đã làm sạch: {cleaned_path}")
    print(f"- Báo cáo EDA: {EDA_DIR}")
    print("  imputation_report.md, imputation_log.csv")
    print("  missing_values_before/after.csv, missingno_*.png (nếu có missingno)")
    print("  before_after_imputation.csv, before_after_categorical.csv, compare_*.png")
    print("  numerical_univariate_stats.csv, outlier_iqr_summary.csv, categorical_frequency.csv")
    print("  hist_*.png, boxplot_*.png")
    print("=" * 68)
 
 
if __name__ == "__main__":
    main()