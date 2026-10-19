
from pathlib import Path

import pandas as pd


# ==========================================
# 1. KHAI BÁO ĐƯỜNG DẪN
# ==========================================

ROOT_DIR = Path(__file__).resolve().parents[2]

DATA_PATH = ROOT_DIR / "data" / "cleaned" / "cleaned_data.csv"

if not DATA_PATH.exists():
    raise FileNotFoundError(
        f"Không tìm thấy dữ liệu: {DATA_PATH}\n"
        "Hãy kiểm tra Mem4 đã tạo cleaned_data.csv chưa."
    )


# ==========================================
# 2. ĐỌC VÀ CHUẨN BỊ DỮ LIỆU
# ==========================================

df = pd.read_csv(DATA_PATH, low_memory=False)

print("=" * 60)
print("MEMBER 5: MULTIVARIATE ANALYSIS")
print("=" * 60)
print(f"Nguồn dữ liệu: {DATA_PATH}")
print(f"Kích thước dữ liệu: {df.shape[0]} dòng x {df.shape[1]} cột")


cot_so = [
    "gbpprice",
    "discount",
    "height",
    "width",
    "spine",
    "weight",
    "salesRank"
]

cot_phan_loai = [
    "category",
    "type"
]

cot_bat_buoc = cot_so + [
    "no_of_pages",
    "category",
    "type"
]

cot_thieu = [
    col for col in cot_bat_buoc
    if col not in df.columns
]

if cot_thieu:
    raise ValueError(
        f"Dữ liệu thiếu các cột cần thiết: {cot_thieu}"
    )


# Chuyển các cột số sang kiểu numeric
for col in cot_so + ["no_of_pages"]:
    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )


# ==========================================
# 3. PHÂN TÍCH SỐ - SỐ
# ==========================================

print("\n" + "=" * 60)
print("1. PHÂN TÍCH SỐ - SỐ")
print("=" * 60)


# Tương quan Pearson
pearson = df[cot_so].corr(
    method="pearson"
)

print("\n=== MA TRẬN TƯƠNG QUAN PEARSON ===")
print(pearson.round(3))


# Tương quan Spearman
spearman = df[cot_so].corr(
    method="spearman"
)

print("\n=== MA TRẬN TƯƠNG QUAN SPEARMAN ===")
print(spearman.round(3))


print("\n=== MỐI QUAN HỆ GIỮA SỐ TRANG VÀ GIÁ ===")

so_trang_gia = df[
    ["no_of_pages", "gbpprice"]
].corr(method="pearson")

print(so_trang_gia.round(3))


print("\n=== GIẢI THÍCH ===")
print(
    "- Pearson đo mức độ và chiều hướng của mối quan hệ tuyến tính."
)
print(
    "- Spearman đo mối quan hệ đơn điệu dựa trên thứ hạng."
)
print(
    "- Tương quan không chứng minh rằng một biến gây ra biến còn lại."
)


# ==========================================
# 4. PHÂN TÍCH PHÂN LOẠI - SỐ
# ==========================================

print("\n" + "=" * 60)
print("2. PHÂN TÍCH PHÂN LOẠI - SỐ")
print("=" * 60)


gia_theo_the_loai = (
    df.dropna(subset=["category", "gbpprice"])
    .groupby("category")["gbpprice"]
    .agg(["count", "mean", "median", "std"])
    .sort_values("mean", ascending=False)
)

gia_theo_the_loai = gia_theo_the_loai.rename(
    columns={
        "count": "Số lượng sách",
        "mean": "Giá trung bình (GBP)",
        "median": "Giá trung vị (GBP)",
        "std": "Độ lệch chuẩn"
    }
)

print("\n=== GIÁ THEO THỂ LOẠI ===")
print(gia_theo_the_loai.round(2).to_string())


print("\n=== TOP 10 THỂ LOẠI CÓ GIÁ TRUNG BÌNH CAO NHẤT ===")
print(gia_theo_the_loai.head(10).round(2).to_string())


if not gia_theo_the_loai.empty:
    top_category = gia_theo_the_loai.index[0]
    top_price = gia_theo_the_loai.iloc[0]["Giá trung bình (GBP)"]

    print(
        f"\nInsight: Thể loại có giá trung bình cao nhất là "
        f"'{top_category}', khoảng {top_price:.2f} GBP."
    )

print(
    "Lưu ý: Cần xem xét số lượng sách trong từng thể loại "
    "trước khi so sánh giá trung bình."
)


# ==========================================
# 5. PHÂN TÍCH PHÂN LOẠI - PHÂN LOẠI
# ==========================================

print("\n" + "=" * 60)
print("3. PHÂN TÍCH PHÂN LOẠI - PHÂN LOẠI")
print("=" * 60)


# Bảng chéo số lượng
the_loai_loai_sach = pd.crosstab(
    df["category"],
    df["type"]
)

# Sắp xếp theo thể loại có nhiều sách nhất
the_loai_loai_sach["Tong_so_sach"] = (
    the_loai_loai_sach.sum(axis=1)
)

the_loai_loai_sach = the_loai_loai_sach.sort_values(
    "Tong_so_sach",
    ascending=False
)

print("\n=== BẢNG CHÉO: THỂ LOẠI VÀ LOẠI SÁCH ===")
print(the_loai_loai_sach.to_string())


# Bảng phân phối phần trăm trong từng thể loại
bang_phan_phoi = pd.crosstab(
    df["category"],
    df["type"],
    normalize="index"
) * 100

# Sắp xếp cùng thứ tự với bảng số lượng
bang_phan_phoi = bang_phan_phoi.reindex(
    the_loai_loai_sach.index
)

print("\n=== BẢNG PHÂN PHỐI (%) TRONG TỪNG THỂ LOẠI ===")
print(bang_phan_phoi.round(2).to_string())


print("\n=== TOP 10 THỂ LOẠI PHỔ BIẾN NHẤT ===")
print(the_loai_loai_sach.head(10).to_string())


# ==========================================
# 6. KẾT THÚC
# ==========================================

print("\n" + "=" * 60)
print("HOÀN THÀNH PHÂN TÍCH ĐA BIẾN")
print("=" * 60)
