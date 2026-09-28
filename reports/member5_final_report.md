
# PHÂN TÍCH DỮ LIỆU 

## 1. Phân tích số - số

### Tương quan Pearson

           gbpprice  discount    ...      weight  salesRank
gbpprice       1.00      0.39    ...        0.49      -0.01
discount       0.39      1.00    ...        0.45      -0.02
height         0.26      0.18    ...        0.35       0.01
width          0.21      0.21    ...        0.40      -0.01
spine          0.27      0.27    ...        0.54      -0.07
weight         0.49      0.45    ...        1.00      -0.02
salesRank     -0.01     -0.02    ...       -0.02       1.00

[7 rows x 7 columns]

### Tương quan Spearman

           gbpprice  discount    ...      weight  salesRank
gbpprice       1.00      0.54    ...        0.69      -0.03
discount       0.54      1.00    ...        0.55      -0.02
height         0.35      0.26    ...        0.39       0.03
width          0.40      0.36    ...        0.47      -0.01
spine          0.34      0.25    ...        0.53      -0.10
weight         0.69      0.55    ...        1.00      -0.01
salesRank     -0.03     -0.02    ...       -0.01       1.00

[7 rows x 7 columns]

### Mối quan hệ giữa số trang và giá

             no_of_pages  gbpprice
no_of_pages         1.00      0.27
gbpprice            0.27      1.00

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

category
politics        36.74
technology      35.46
medical         30.87
computing       29.20
business        22.74
artanddesign    21.31
languages       21.12
stage           19.36
socsci          18.21
education       17.17
Name: gbpprice, dtype: float64

### So What?

Giá trung bình có sự khác nhau giữa các thể loại.
Kết quả này giúp so sánh mức giá giữa các nhóm.


## 3. Phân tích phân loại - phân loại

### Bảng chéo giữa thể loại và loại sách

type           Bath Book          ...          Spiral / Comb ... 
category                          ...                            
artanddesign            0         ...                           2
biography               0         ...                           0
business                0         ...                           0
childrens               2         ...                           2
computing               0         ...                           0
crime                   0         ...                           0
education               0         ...                           2
fiction                 0         ...                           0
foodanddrink            0         ...                           1
graphicnovels           0         ...                           0

[10 rows x 19 columns]

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
