
from pathlib import Path

import pandas as pd


# ==========================================
# 1. KHAI BÁO ĐƯỜNG DẪN
# ==========================================

ROOT_DIR = Path(__file__).resolve().parents[2]

DATA_PATH = ROOT_DIR / "data" / "cleaned" / "cleaned_data.csv"
REPORT_DIR = ROOT_DIR / "reports"
REPORT_PATH = REPORT_DIR / "member5_final_report.md"

REPORT_DIR.mkdir(parents=True, exist_ok=True)


# ==========================================
# 2. ĐỌC VÀ KIỂM TRA DỮ LIỆU
# ==========================================

if not DATA_PATH.exists():
    raise FileNotFoundError(
        f"Không tìm thấy dữ liệu: {DATA_PATH}\n"
        "Hãy kiểm tra Mem4 đã tạo cleaned_data.csv chưa."
    )

df = pd.read_csv(DATA_PATH, low_memory=False)

print("=" * 60)
print("MEMBER 5: MULTIVARIATE ANALYSIS + INSIGHTS")
print("=" * 60)
print(f"Dữ liệu: {DATA_PATH}")
print(f"Kích thước: {df.shape[0]} dòng x {df.shape[1]} cột")


# Kiểm tra các cột cần sử dụng
cot_so = [
    "gbpprice",
    "discount",
    "height",
    "width",
    "spine",
    "weight",
    "salesRank"
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
        f"Dữ liệu thiếu các cột: {cot_thieu}"
    )


# Chuyển các cột số sang kiểu numeric
for col in cot_so + ["no_of_pages"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")


# ==========================================
# 3. PHÂN TÍCH SỐ - SỐ
# ==========================================

# Pearson: đo tương quan tuyến tính
pearson = df[cot_so].corr(method="pearson")

# Spearman: đo tương quan đơn điệu dựa trên thứ hạng
spearman = df[cot_so].corr(method="spearman")

# Mối quan hệ giữa số trang và giá
so_trang_gia = df[
    ["no_of_pages", "gbpprice"]
].corr(method="pearson")


# ==========================================
# 4. PHÂN TÍCH PHÂN LOẠI - SỐ
# ==========================================

gia_theo_the_loai = (
    df.dropna(subset=["category", "gbpprice"])
    .groupby("category")["gbpprice"]
    .agg(["mean", "median", "count"])
    .sort_values("mean", ascending=False)
)

gia_theo_the_loai = gia_theo_the_loai.rename(
    columns={
        "mean": "Giá trung bình (GBP)",
        "median": "Giá trung vị (GBP)",
        "count": "Số lượng sách"
    }
)


# ==========================================
# 5. PHÂN TÍCH PHÂN LOẠI - PHÂN LOẠI
# ==========================================

the_loai_loai_sach = pd.crosstab(
    df["category"],
    df["type"]
)

# Sắp xếp theo tổng số sách của mỗi thể loại
the_loai_loai_sach = (
    the_loai_loai_sach
    .assign(Tong_so_sach=the_loai_loai_sach.sum(axis=1))
    .sort_values("Tong_so_sach", ascending=False)
)

# Bảng hiển thị 10 thể loại phổ biến nhất
top_10_the_loai = the_loai_loai_sach.head(10)


# ==========================================
# 6. TẠO NHẬN XÉT TỪ KẾT QUẢ THỰC TẾ
# ==========================================

# Tìm cặp biến có tương quan mạnh nhất,
# không tính tương quan của một biến với chính nó
pearson_pairs = pearson.where(
    ~pd.DataFrame(
        [[i == j for j in pearson.columns]
         for i in pearson.index],
        index=pearson.index,
        columns=pearson.columns
    )
).stack()

if not pearson_pairs.empty:
    strongest_pair = pearson_pairs.abs().idxmax()
    strongest_value = pearson.loc[
        strongest_pair[0], strongest_pair[1]
    ]

    if strongest_value > 0:
        relation = "tương quan thuận"
    elif strongest_value < 0:
        relation = "tương quan nghịch"
    else:
        relation = "không có tương quan tuyến tính"

    pearson_insight = (
        f"Cặp biến có tương quan Pearson mạnh nhất là "
        f"**{strongest_pair[0]}** và **{strongest_pair[1]}**, "
        f"hệ số tương quan = **{strongest_value:.2f}** "
        f"({relation})."
    )
else:
    pearson_insight = (
        "Chưa đủ dữ liệu hợp lệ để xác định cặp biến "
        "có tương quan Pearson mạnh nhất."
    )


if (
    so_trang_gia.notna().all().all()
    and pd.notna(so_trang_gia.loc["no_of_pages", "gbpprice"])
):
    page_price_corr = so_trang_gia.loc[
        "no_of_pages", "gbpprice"
    ]

    page_price_insight = (
        f"Hệ số tương quan Pearson giữa số trang và giá sách "
        f"là **{page_price_corr:.2f}**."
    )
else:
    page_price_insight = (
        "Chưa đủ dữ liệu hợp lệ để tính tương quan "
        "giữa số trang và giá sách."
    )


if not gia_theo_the_loai.empty:
    highest_category = gia_theo_the_loai.index[0]
    highest_price = gia_theo_the_loai.iloc[0][
        "Giá trung bình (GBP)"
    ]

    category_insight = (
        f"Trong các thể loại có dữ liệu giá hợp lệ, "
        f"**{highest_category}** có giá trung bình cao nhất "
        f"là **{highest_price:.2f} GBP**. "
        "Cần lưu ý số lượng sách ở từng thể loại khi so sánh."
    )
else:
    category_insight = (
        "Chưa đủ dữ liệu hợp lệ để so sánh giá trung bình "
        "giữa các thể loại."
    )


# ==========================================
# 7. TẠO BÁO CÁO MARKDOWN
# ==========================================

bao_cao = f"""
# BÁO CÁO PHÂN TÍCH ĐA BIẾN VÀ INSIGHT

## Thông tin dữ liệu

- Nguồn dữ liệu: `data/cleaned/cleaned_data.csv`
- Số dòng: {df.shape[0]:,}
- Số cột: {df.shape[1]:,}

## 1. Phân tích số - số

### Tương quan Pearson

{pearson.round(2).to_markdown()}

### Tương quan Spearman

{spearman.round(2).to_markdown()}

### Mối quan hệ giữa số trang và giá sách

{so_trang_gia.round(2).to_markdown()}

### So What?

- Pearson đo mức độ và chiều hướng của mối quan hệ tuyến tính.
- Spearman đánh giá mối quan hệ đơn điệu dựa trên thứ hạng.
- Tương quan không chứng minh quan hệ nhân quả.

**Insight từ dữ liệu:** {pearson_insight}

**Số trang và giá sách:** {page_price_insight}

## 2. Phân tích phân loại - số

### Giá theo thể loại

{gia_theo_the_loai.head(10).round(2).to_markdown()}

### So What?

Bảng này cho phép so sánh giá trung bình, giá trung vị và
số lượng sách giữa các thể loại. Giá trung bình có thể bị
ảnh hưởng bởi những cuốn sách có giá đặc biệt cao hoặc thấp.

**Insight từ dữ liệu:** {category_insight}

## 3. Phân tích phân loại - phân loại

### Bảng chéo giữa thể loại và loại sách

{top_10_the_loai.to_markdown()}

### So What?

Bảng chéo cho biết số lượng sách thuộc từng loại trong mỗi
thể loại. Các thể loại có tổng số sách lớn hơn có thể xuất hiện
nhiều hơn do số lượng dữ liệu ban đầu khác nhau.

## 4. Phân tích trực quan

Các biểu đồ được tạo bởi `src/analysis/data_visualization.py`:

1. Ma trận tương quan.
2. Biểu đồ phân tán giữa số trang và giá.
3. Giá trung bình theo thể loại.
4. Biểu đồ hộp giá theo thể loại.
5. Biểu đồ cột chồng theo thể loại và loại sách.
6. Histogram + KDE của giá sách.
7. Biểu đồ hộp giá sách.
8. Top 10 nhà xuất bản có nhiều sách nhất.
9. Biểu đồ tròn về các loại sách phổ biến nhất.

Thư mục biểu đồ: `visualization/`

### So What?

Các biểu đồ hỗ trợ quan sát tương quan, phân phối giá,
sự khác biệt giữa các nhóm và những điểm dữ liệu có thể là ngoại lệ.
Cần xem biểu đồ thực tế trước khi đưa ra kết luận cụ thể.

## 5. Ý nghĩa đối với AI/ML

- Tương quan có thể hỗ trợ khảo sát và lựa chọn đặc trưng.
- Biến phân loại cần được mã hóa trước khi đưa vào nhiều mô hình ML.
- Có thể thử Linear Regression nếu quan hệ tuyến tính và các giả định
  của mô hình phù hợp.
- Có thể thử Decision Tree hoặc Random Forest để khảo sát
  các quan hệ phi tuyến.
- Cần kiểm tra dữ liệu thiếu, ngoại lệ và rò rỉ dữ liệu trước khi huấn luyện.
- Không nên loại bỏ biến chỉ dựa vào hệ số tương quan mà chưa xét mục tiêu
  dự đoán và ý nghĩa của biến.

## 6. Kết luận

Phân tích gồm ba nhóm chính:

- Số - số: khảo sát tương quan giữa các biến số.
- Phân loại - số: so sánh giá giữa các thể loại.
- Phân loại - phân loại: khảo sát số lượng loại sách theo thể loại.

Các kết quả trên hỗ trợ hiểu dữ liệu và định hướng bước xây dựng mô hình.
Cần dựa vào bảng kết quả và biểu đồ thực tế để đưa ra insight cuối cùng.
"""


# ==========================================
# 8. LƯU BÁO CÁO
# ==========================================

with open(REPORT_PATH, "w", encoding="utf-8") as file:
    file.write(bao_cao)

print("\nĐã tạo báo cáo thành công!")
print(f"Báo cáo được lưu tại: {REPORT_PATH}")
