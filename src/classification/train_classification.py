
from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier


ROOT = Path(__file__).resolve().parents[2]
TARGET = "category"
NUMERIC_FEATURES = [
    "gbpprice",
    "discount",
    "no_of_pages",
    "height",
    "width",
    "spine",
    "weight",
    "salesRank",
    "original_price",
    "discount_price",
    "discount_percentage",
    "rating",
    "rating_count",
]
CATEGORICAL_FEATURES = ["type", "language", "published_country"]


def find_dataset(user_path: str | None) -> Path:
    """Find the CSV from a supplied path or common project locations."""
    if user_path:
        path = Path(user_path)
        if not path.is_absolute():
            path = ROOT / path
        if path.exists():
            return path
        raise FileNotFoundError(f"Không tìm thấy dataset: {path}")

    candidates = [
        ROOT / "data" / "processed" / "cleaned_data.csv",
        ROOT / "data" / "processed" / "cleaned_data(1).csv",
        ROOT / "data" / "cleaned_data.csv",
        ROOT / "cleaned_data.csv",
    ]
    for path in candidates:
        if path.exists():
            return path
    raise FileNotFoundError(
        "Không tìm thấy cleaned_data.csv. Hãy đặt file tại data/processed/cleaned_data.csv "
        "hoặc chạy với --data <đường_dẫn_file>."
    )


def prepare_data(df: pd.DataFrame):
    """Select suitable features and prepare the target/features."""
    if TARGET not in df.columns:
        raise ValueError(f"Dataset phải có cột target '{TARGET}'.")

    feature_columns = [
        c for c in NUMERIC_FEATURES + CATEGORICAL_FEATURES if c in df.columns
    ]
    if not feature_columns:
        raise ValueError("Không tìm thấy các feature đã cấu hình trong dataset.")

    data = df[feature_columns + [TARGET]].copy()
    # Treat placeholder strings as missing values for selected columns.
    data.replace(["Unknown", "unknown", "UNKNOWN", ""], np.nan, inplace=True)

    # Some numeric-looking columns, such as no_of_pages, are stored as text.
    for col in NUMERIC_FEATURES:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors="coerce")

    # A row without its target cannot be used for supervised training.
    data = data.dropna(subset=[TARGET])
    data[TARGET] = data[TARGET].astype(str).str.strip()
    data = data[data[TARGET] != ""]

    X = data[feature_columns].copy()
    y = data[TARGET].copy()
    numeric_cols = [c for c in NUMERIC_FEATURES if c in X.columns]
    categorical_cols = [c for c in CATEGORICAL_FEATURES if c in X.columns]
    return X, y, numeric_cols, categorical_cols


def build_preprocessor(numeric_cols: list[str], categorical_cols: list[str]):
    transformers = []
    if numeric_cols:
        numeric_pipeline = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
            ]
        )
        transformers.append(("numeric", numeric_pipeline, numeric_cols))
    if categorical_cols:
        categorical_pipeline = Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="most_frequent")),
                ("onehot", OneHotEncoder(handle_unknown="ignore")),
            ]
        )
        transformers.append(("categorical", categorical_pipeline, categorical_cols))
    return ColumnTransformer(transformers=transformers, remainder="drop")


def main():
    parser = argparse.ArgumentParser(description="Train Member 4 classification models")
    parser.add_argument("--data", type=str, default=None, help="Path to cleaned CSV")
    parser.add_argument("--target", type=str, default="category", help="Target column (default: category)")
    args = parser.parse_args()

    global TARGET
    TARGET = args.target

    data_path = find_dataset(args.data)
    print(f"Đang đọc dữ liệu: {data_path}")
    df = pd.read_csv(data_path)
    print(f"Kích thước dataset: {df.shape[0]} dòng x {df.shape[1]} cột")

    X, y, numeric_cols, categorical_cols = prepare_data(df)
    if y.nunique() < 2:
        raise ValueError("Target cần có ít nhất 2 lớp để huấn luyện mô hình phân loại.")

    output_model = ROOT / "models" / "classification"
    output_viz = ROOT / "visualization" / "stage2" / "classification"
    output_report = ROOT / "reports" / "stage2"
    for folder in (output_model, output_viz, output_report):
        folder.mkdir(parents=True, exist_ok=True)

    class_counts = y.value_counts().sort_values(ascending=False)
    class_counts.rename_axis(TARGET).reset_index(name="count").to_csv(
        output_report / "classification_class_distribution.csv", index=False
    )
    imbalance_ratio = float(class_counts.min() / class_counts.max())
    use_balanced = imbalance_ratio < 0.5
    class_weight = "balanced" if use_balanced else None

    print("\nPhân bố target:")
    print(class_counts.to_string())
    print(f"Tỷ lệ lớp nhỏ nhất/lớn nhất: {imbalance_ratio:.3f}")
    print(f"Dùng class_weight='balanced': {use_balanced}")

    # Stratification keeps the class proportions similar in train and test.
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    model_specs = {
        "Logistic Regression": LogisticRegression(
            max_iter=2000,
            class_weight=class_weight,
            random_state=42,
        ),
        "Decision Tree": DecisionTreeClassifier(
            class_weight=class_weight,
            random_state=42,
            max_depth=20,
            min_samples_leaf=2,
        ),
    }

    labels = sorted(y.unique())
    results = []
    fitted_models = {}

    for model_name, classifier in model_specs.items():
        pipeline = Pipeline(
            steps=[
                ("preprocessor", build_preprocessor(numeric_cols, categorical_cols)),
                ("classifier", classifier),
            ]
        )
        print(f"\nĐang huấn luyện: {model_name}")
        pipeline.fit(X_train, y_train)
        predictions = pipeline.predict(X_test)
        fitted_models[model_name] = pipeline

        metrics = {
            "model": model_name,
            "accuracy": accuracy_score(y_test, predictions),
            "precision_macro": precision_score(y_test, predictions, average="macro", zero_division=0),
            "recall_macro": recall_score(y_test, predictions, average="macro", zero_division=0),
            "f1_macro": f1_score(y_test, predictions, average="macro", zero_division=0),
            "f1_weighted": f1_score(y_test, predictions, average="weighted", zero_division=0),
        }
        results.append(metrics)
        print(pd.Series(metrics).to_string())
        print("\nClassification report:")
        print(classification_report(y_test, predictions, zero_division=0))

        # Save one confusion matrix per model.
        cm = confusion_matrix(y_test, predictions, labels=labels)
        plt.figure(figsize=(max(10, len(labels) * 0.45), max(8, len(labels) * 0.38)))
        sns.heatmap(
            cm,
            cmap="Blues",
            annot=(len(labels) <= 12),
            fmt="d",
            xticklabels=labels,
            yticklabels=labels,
        )
        plt.title(f"Confusion Matrix - {model_name}")
        plt.xlabel("Predicted label")
        plt.ylabel("True label")
        plt.xticks(rotation=90, fontsize=7)
        plt.yticks(rotation=0, fontsize=7)
        plt.tight_layout()
        file_stub = "logistic_regression" if model_name == "Logistic Regression" else "decision_tree"
        plt.savefig(output_viz / f"confusion_matrix_{file_stub}.png", dpi=180)
        plt.close()

        # Save the detailed per-class report as CSV.
        report_dict = classification_report(
            y_test, predictions, output_dict=True, zero_division=0
        )
        pd.DataFrame(report_dict).transpose().to_csv(
            output_report / f"classification_report_{file_stub}.csv", index=True
        )

    metrics_df = pd.DataFrame(results).sort_values(
        by=["f1_macro", "accuracy"], ascending=False
    )
    metrics_df.to_csv(output_report / "classification_metrics.csv", index=False)

    # Macro F1 is the primary selection metric for a multi-class target.
    best_name = metrics_df.iloc[0]["model"]
    best_pipeline = fitted_models[best_name]
    joblib.dump(best_pipeline, output_model / "best_model.joblib")

    metadata = {
        "target": TARGET,
        "best_model": best_name,
        "selection_metric": "f1_macro",
        "input_features": list(X.columns),
        "numeric_features": numeric_cols,
        "categorical_features": categorical_cols,
        "classes": labels,
        "test_size": 0.2,
        "random_state": 42,
        "class_weight": class_weight,
        "dataset_path_used": str(data_path),
        "note": "Loaded model is a complete sklearn Pipeline including preprocessing.",
    }
    with open(output_model / "model_metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    # Generate the report with the real metrics from this run.
    report_lines = [
        "# Classification Analysis - Member 4",
        "",
        f"- **Dataset:** `{data_path.name}`",
        f"- **Số dòng dùng được:** {len(X)}",
        f"- **Target:** `{TARGET}`",
        f"- **Số lớp:** {y.nunique()}",
        f"- **Feature đầu vào:** {', '.join(X.columns)}",
        f"- **Tỷ lệ lớp nhỏ nhất/lớn nhất:** {imbalance_ratio:.3f}",
        f"- **Xử lý mất cân bằng:** {'class_weight=balanced' if use_balanced else 'Không bật class_weight vì phân bố lớp chưa cho thấy mất cân bằng nghiêm trọng theo ngưỡng 0.5'}",
        "",
        "## 1. Phương pháp",
        "Dữ liệu được chia thành 80% train và 20% test với `stratify=y`, `random_state=42`. "
        "Các feature số được điền thiếu bằng median và chuẩn hóa StandardScaler; feature phân loại "
        "được điền thiếu bằng mode và mã hóa OneHotEncoder. Các bước tiền xử lý được đặt trong Pipeline "
        "để chỉ fit trên tập train.",
        "",
        "## 2. Kết quả so sánh",
        metrics_df.to_markdown(index=False, floatfmt=".4f"),
        "",
        f"## 3. Mô hình được chọn\nMô hình tốt nhất theo **Macro F1-score** (dùng Accuracy làm tiêu chí phụ khi hòa) là **{best_name}**. Model và preprocessing được lưu tại `models/classification/best_model.joblib`.",
        "",
        "## 4. Biểu đồ",
        "- `visualization/stage2/classification/confusion_matrix_logistic_regression.png`",
        "- `visualization/stage2/classification/confusion_matrix_decision_tree.png`",
        "",
        "## 5. Hạn chế và lưu ý",
        "- Target `category` được chọn làm bài toán phân loại nhiều lớp; cần xác nhận đây là mục tiêu phù hợp với câu hỏi kinh doanh của nhóm.",
        "- Một số cột mô tả văn bản, ID, tên sách và các cột tiếng Việt bị lặp/không đồng nhất không được đưa vào mô hình.",
        "- Kết quả chỉ phản ánh tập test của lần chia dữ liệu này; không khẳng định quan hệ nhân quả.",
        "- Trước khi triển khai, cần kiểm thử dữ liệu mới có đúng các feature đầu vào được ghi trong `model_metadata.json`.",
        "",
        "## 6. Bàn giao cho Member 5",
        "Nạp `models/classification/best_model.joblib` bằng `joblib.load(...)`. Đây là Pipeline hoàn chỉnh; gọi `predict()` trực tiếp trên DataFrame chứa các cột trong `input_features` của `model_metadata.json`.",
    ]
    (output_report / "classification_analysis.md").write_text(
        "\n".join(report_lines), encoding="utf-8"
    )

    print("\n=== KẾT QUẢ CUỐI ===")
    print(metrics_df.to_string(index=False))
    print(f"Best model: {best_name}")
    print(f"Đã lưu model: {output_model / 'best_model.joblib'}")
    print(f"Đã lưu báo cáo: {output_report / 'classification_analysis.md'}")


if __name__ == "__main__":
    main()
