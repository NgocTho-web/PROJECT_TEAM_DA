import pandas as pd

df = pd.read_csv("data/blackwell_shop_cleaned.csv")

# ==============================
# 1. Phân tích số - số
# ==============================

cot_so = [
    "gbpprice",
    "discount",
    "height",
    "width",
    "spine",
    "weight",
    "salesRank"
]

print("=== MA TRẬN TƯƠNG QUAN PEARSON ===")
print(df[cot_so].corr(method="pearson"))

print("\n=== MA TRẬN TƯƠNG QUAN SPEARMAN ===")
print(df[cot_so].corr(method="spearman"))

# Phân tích số trang và giá
df["no_of_pages"] = pd.to_numeric(
    df["no_of_pages"],
    errors="coerce"
)

print("\n=== MỐI QUAN HỆ GIỮA SỐ TRANG VÀ GIÁ ===")
print(df[["no_of_pages", "gbpprice"]].corr())

print("\nPearson và Spearman được dùng để xem xu hướng")
print("giữa các biến là tuyến tính hay có sự khác biệt.")

# ==============================
# 2. Phân tích phân loại - số
# ==============================

print("\n=== GIÁ THEO THỂ LOẠI ===")

print(
    df.groupby("category")["gbpprice"].agg(
        ["count", "mean", "median", "std"]
    )
)

# ==============================
# 3. Phân tích phân loại - phân loại
# ==============================

print("\n=== THỂ LOẠI VÀ LOẠI SÁCH ===")

print(
    pd.crosstab(
        df["category"],
        df["type"]
    )
)

print("\n=== BẢNG PHÂN PHỐI (%) ===")

print(
    pd.crosstab(
        df["category"],
        df["type"],
        normalize="index"
    ) * 100
)