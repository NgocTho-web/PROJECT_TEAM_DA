
from pathlib import Path

import pandas as pd
import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import seaborn as sns


# ==========================================
# 1. KHAI BÁO ĐƯỜNG DẪN
# ==========================================

ROOT_DIR = Path(__file__).resolve().parents[2]

DATA_PATH = ROOT_DIR / "data" / "cleaned" / "cleaned_data.csv"
OUTPUT_DIR = ROOT_DIR / "visualization"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid")


# ==========================================
# 2. ĐỌC VÀ CHUẨN BỊ DỮ LIỆU
# ==========================================

if not DATA_PATH.exists():
    raise FileNotFoundError(
        f"Không tìm thấy file dữ liệu: {DATA_PATH}\n"
        "Hãy kiểm tra Mem4 đã tạo cleaned_data.csv chưa."
    )

df = pd.read_csv(DATA_PATH, low_memory=False)

print("=" * 60)
print("MEMBER 5: MULTIVARIATE ANALYSIS + DATA VISUALIZATION")
print("=" * 60)
print(f"File dữ liệu: {DATA_PATH}")
print(f"Kích thước dữ liệu: {df.shape[0]} dòng x {df.shape[1]} cột")


# Các cột số cần dùng trong biểu đồ
numeric_columns = [
    "gbpprice",
    "discount",
    "height",
    "width",
    "spine",
    "weight",
    "salesRank",
    "no_of_pages"
]

# Chuyển dữ liệu số về kiểu numeric
for col in numeric_columns:
    if col in df.columns:
        df[col] = pd.to_numeric(
            df[col]
            .astype("string")
            .str.replace(",", "", regex=False)
            .str.replace("£", "", regex=False)
            .str.strip(),
            errors="coerce"
        )

# Kiểm tra các cột cần thiết
required_columns = [
    "gbpprice",
    "no_of_pages",
    "category",
    "type",
    "publisher"
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Dataset thiếu các cột cần thiết: {missing_columns}"
    )

# Chuẩn hóa giá trị thiếu ở các cột phân loại
for col in ["category", "type", "publisher"]:
    df[col] = (
        df[col]
        .astype("string")
        .str.strip()
        .replace("", pd.NA)
    )


# ==========================================
# 3. BIỂU ĐỒ NHIỆT TƯƠNG QUAN
# ==========================================

print("\n1. Vẽ correlation heatmap...")

corr_columns = [
    "gbpprice",
    "discount",
    "height",
    "width",
    "spine",
    "weight",
    "salesRank"
]

corr_columns = [
    col for col in corr_columns
    if col in df.columns
    and df[col].notna().sum() > 1
]

corr_data = df[corr_columns].corr()

plt.figure(figsize=(10, 7))

sns.heatmap(
    corr_data,
    annot=True,
    fmt=".2f",
    cmap="coolwarm",
    center=0
)

plt.title("Ma trận tương quan giữa các biến số")
plt.xlabel("Các biến số")
plt.ylabel("Các biến số")
plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "01_correlation_heatmap.png",
    dpi=300,
    bbox_inches="tight"
)
plt.close()


# ==========================================
# 4. BIỂU ĐỒ PHÂN TÁN
# ==========================================

print("2. Vẽ scatter plot...")

scatter_data = df[
    ["no_of_pages", "gbpprice"]
].dropna()

plt.figure(figsize=(8, 5))

sns.scatterplot(
    data=scatter_data,
    x="no_of_pages",
    y="gbpprice",
    alpha=0.6
)

plt.title("Mối quan hệ giữa số trang và giá sách")
plt.xlabel("Số trang")
plt.ylabel("Giá (GBP)")
plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "02_scatter_plot.png",
    dpi=300,
    bbox_inches="tight"
)
plt.close()


# ==========================================
# 5. BIỂU ĐỒ CỘT GIÁ TRUNG BÌNH THEO THỂ LOẠI
# ==========================================

print("3. Vẽ bar chart giá trung bình theo thể loại...")

gia_theo_the_loai = (
    df.dropna(subset=["category", "gbpprice"])
    .groupby("category")["gbpprice"]
    .mean()
    .sort_values(ascending=False)
    .head(10)
)

plt.figure(figsize=(10, 5))

gia_theo_the_loai.plot(kind="bar")

plt.title("Top 10 thể loại có giá trung bình cao nhất")
plt.xlabel("Thể loại")
plt.ylabel("Giá trung bình (GBP)")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "03_average_price_by_category.png",
    dpi=300,
    bbox_inches="tight"
)
plt.close()


# ==========================================
# 6. BIỂU ĐỒ HỘP GIÁ THEO THỂ LOẠI
# ==========================================

print("4. Vẽ grouped box plot...")

the_loai_top = (
    df["category"]
    .dropna()
    .value_counts()
    .head(10)
    .index
)

box_data = df[
    df["category"].isin(the_loai_top)
].dropna(subset=["category", "gbpprice"])

plt.figure(figsize=(12, 6))

sns.boxplot(
    data=box_data,
    x="category",
    y="gbpprice"
)

plt.title("Phân bố giá sách theo 10 thể loại phổ biến nhất")
plt.xlabel("Thể loại")
plt.ylabel("Giá (GBP)")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "04_grouped_box_plot.png",
    dpi=300,
    bbox_inches="tight"
)
plt.close()


# ==========================================
# 7. BIỂU ĐỒ CỘT CHỒNG
# ==========================================

print("5. Vẽ stacked bar chart...")

top_categories = (
    df["category"]
    .dropna()
    .value_counts()
    .head(10)
    .index
)

stacked_data = df[
    df["category"].isin(top_categories)
].dropna(subset=["category", "type"])

bang = pd.crosstab(
    stacked_data["category"],
    stacked_data["type"]
)

plt.figure(figsize=(12, 6))

bang.plot(
    kind="bar",
    stacked=True,
    figsize=(12, 6)
)

plt.title("Phân bố loại sách theo thể loại")
plt.xlabel("Thể loại")
plt.ylabel("Số lượng sách")
plt.xticks(rotation=45, ha="right")
plt.legend(title="Loại sách", bbox_to_anchor=(1.02, 1))
plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "05_stacked_bar_chart.png",
    dpi=300,
    bbox_inches="tight"
)
plt.close()


# ==========================================
# 8. HISTOGRAM + KDE
# ==========================================

print("6. Vẽ histogram và KDE...")

price_data = df["gbpprice"].dropna()

plt.figure(figsize=(8, 5))

sns.histplot(
    price_data,
    kde=True
)

plt.title("Phân bố giá sách")
plt.xlabel("Giá (GBP)")
plt.ylabel("Tần số")
plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "06_histogram_kde.png",
    dpi=300,
    bbox_inches="tight"
)
plt.close()


# ==========================================
# 9. BOXPLOT GIÁ SÁCH
# ==========================================

print("7. Vẽ box plot giá sách...")

plt.figure(figsize=(8, 4))

sns.boxplot(
    x=price_data
)

plt.title("Biểu đồ hộp của giá sách")
plt.xlabel("Giá (GBP)")
plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "07_box_plot_price.png",
    dpi=300,
    bbox_inches="tight"
)
plt.close()


# ==========================================
# 10. TOP 10 NHÀ XUẤT BẢN
# ==========================================

print("8. Vẽ biểu đồ nhà xuất bản...")

nha_xuat_ban = (
    df["publisher"]
    .dropna()
    .value_counts()
    .head(10)
)

plt.figure(figsize=(10, 5))

nha_xuat_ban.plot(kind="bar")

plt.title("Top 10 nhà xuất bản có nhiều sách nhất")
plt.xlabel("Nhà xuất bản")
plt.ylabel("Số lượng sách")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "08_bar_chart_publishers.png",
    dpi=300,
    bbox_inches="tight"
)
plt.close()


# ==========================================
# 11. BIỂU ĐỒ TRÒN
# ==========================================

print("9. Vẽ biểu đồ tròn loại sách...")

loai_sach = (
    df["type"]
    .dropna()
    .value_counts()
    .head(5)
)

plt.figure(figsize=(8, 8))

loai_sach.plot(
    kind="pie",
    autopct="%1.1f%%",
    startangle=90
)

plt.title("Tỷ lệ 5 loại sách phổ biến nhất")
plt.ylabel("")
plt.tight_layout()

plt.savefig(
    OUTPUT_DIR / "09_pie_chart_types.png",
    dpi=300,
    bbox_inches="tight"
)
plt.close()


# ==========================================
# 12. HOÀN TẤT
# ==========================================

print("\n" + "=" * 60)
print("ĐÃ HOÀN THÀNH TRỰC QUAN HÓA DỮ LIỆU")
print("=" * 60)
print(f"Thư mục lưu biểu đồ: {OUTPUT_DIR}")
print("Tổng số biểu đồ dự kiến: 9")

for file in sorted(OUTPUT_DIR.glob("*.png")):
    print(f"- {file.name}")
