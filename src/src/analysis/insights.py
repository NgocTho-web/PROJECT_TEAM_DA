import pandas as pd

df = pd.read_csv("data/blackwell_shop_cleaned.csv")

df["no_of_pages"] = pd.to_numeric(
    df["no_of_pages"],
    errors="coerce"
)


# Tính toán kết quả

cot_so = [
    "gbpprice",
    "discount",
    "height",
    "width",
    "spine",
    "weight",
    "salesRank"
]

pearson = df[cot_so].corr(
    method="pearson"
)

spearman = df[cot_so].corr(
    method="spearman"
)

so_trang_gia = df[
    ["no_of_pages", "gbpprice"]
].corr()

gia_theo_the_loai = (
    df.groupby("category")["gbpprice"]
    .mean()
    .sort_values(ascending=False)
)

the_loai_loai_sach = pd.crosstab(
    df["category"],
    df["type"]
)



# Tạo báo cáo

bao_cao = f"""
# PHÂN TÍCH DỮ LIỆU 

## 1. Phân tích số - số

### Tương quan Pearson

{pearson.round(2)}

### Tương quan Spearman

{spearman.round(2)}

### Mối quan hệ giữa số trang và giá

{so_trang_gia.round(2)}

### So What?

Ma trận tương quan cho biết mức độ liên hệ
giữa các biến số.

Pearson tập trung vào mối quan hệ tuyến tính,
trong khi Spearman giúp xem xét xu hướng tăng
hoặc giảm giữa các biến.

Nếu hai kết quả gần nhau, mối quan hệ có xu hướng
ổn định. Nếu khác nhau nhiều, có thể tồn tại
mối quan hệ phi tuyến hoặc ảnh hưởng của giá trị ngoại lệ.


## 2. Phân tích phân loại - số

### Giá trung bình theo thể loại

{gia_theo_the_loai.head(10).round(2)}

### So What?

Giá trung bình có sự khác nhau giữa các thể loại.
Kết quả này giúp so sánh mức giá giữa các nhóm.


## 3. Phân tích phân loại - phân loại

### Bảng chéo giữa thể loại và loại sách

{the_loai_loai_sach.head(10)}

### So What?

Bảng chéo cho biết số lượng từng loại sách
trong mỗi thể loại.

Từ đó có thể nhận biết nhóm nào xuất hiện
nhiều hoặc ít hơn.


## 4. Phân tích trực quan

Các biểu đồ được sử dụng gồm:

- Ma trận tương quan
- Biểu đồ phân tán
- Biểu đồ cột nhóm
- Biểu đồ hộp theo nhóm
- Biểu đồ cột chồng
- Histogram + KDE
- Biểu đồ hộp
- Biểu đồ cột
- Biểu đồ tròn

### So What?

Các biểu đồ giúp trình bày dữ liệu trực quan hơn,
dễ nhận biết xu hướng, phân bố dữ liệu
và sự khác nhau giữa các nhóm.


## 5. Ý nghĩa đối với AI/ML

- Tương quan có thể hỗ trợ lựa chọn đặc trưng.
- Biến phân loại cần được mã hóa trước khi xây dựng mô hình.
- Quan hệ tuyến tính có thể thử Linear Regression.
- Quan hệ phi tuyến có thể thử Decision Tree hoặc Random Forest.
- Cần kiểm tra giá trị ngoại lệ trước khi xây dựng mô hình.


## 6. Kết luận

Phân tích dữ liệu gồm ba nhóm chính:

- Phân tích số - số
- Phân tích phân loại - số
- Phân tích phân loại - phân loại

Các biểu đồ giúp làm rõ mối quan hệ,
phân bố và sự khác biệt trong dữ liệu.

Kết quả phân tích có thể hỗ trợ lựa chọn
đặc trưng và mô hình AI/ML phù hợp.
"""

with open(
    "reports/member5_final_report.md",
    "w",
    encoding="utf-8"
) as file:

    file.write(bao_cao)

print("Đã tạo báo cáo thành công!")