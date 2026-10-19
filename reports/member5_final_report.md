
# BÁO CÁO PHÂN TÍCH ĐA BIẾN VÀ INSIGHT

## Thông tin dữ liệu

- Nguồn dữ liệu: `data/cleaned/cleaned_data.csv`
- Số dòng: 12,133
- Số cột: 42

## 1. Phân tích số - số

### Tương quan Pearson

|           |   gbpprice |   discount |   height |   width |   spine |   weight |   salesRank |
|:----------|-----------:|-----------:|---------:|--------:|--------:|---------:|------------:|
| gbpprice  |       1    |      -0.03 |    -0.01 |    0    |   -0.01 |    -0.04 |       -0.03 |
| discount  |      -0.03 |       1    |     0.18 |    0.21 |    0.27 |     0.45 |       -0.03 |
| height    |      -0.01 |       0.18 |     1    |    0.13 |   -0.09 |     0.35 |        0    |
| width     |       0    |       0.21 |     0.13 |    1    |    0.08 |     0.4  |       -0.02 |
| spine     |      -0.01 |       0.27 |    -0.09 |    0.08 |    1    |     0.54 |       -0.04 |
| weight    |      -0.04 |       0.45 |     0.35 |    0.4  |    0.54 |     1    |       -0.01 |
| salesRank |      -0.03 |      -0.03 |     0    |   -0.02 |   -0.04 |    -0.01 |        1    |

### Tương quan Spearman

|           |   gbpprice |   discount |   height |   width |   spine |   weight |   salesRank |
|:----------|-----------:|-----------:|---------:|--------:|--------:|---------:|------------:|
| gbpprice  |       1    |       0.51 |     0.32 |    0.38 |    0.31 |     0.64 |       -0.02 |
| discount  |       0.51 |       1    |     0.26 |    0.37 |    0.24 |     0.55 |       -0.01 |
| height    |       0.32 |       0.26 |     1    |    0.09 |   -0.14 |     0.38 |        0.02 |
| width     |       0.38 |       0.37 |     0.09 |    1    |    0.11 |     0.47 |       -0    |
| spine     |       0.31 |       0.24 |    -0.14 |    0.11 |    1    |     0.51 |       -0.07 |
| weight    |       0.64 |       0.55 |     0.38 |    0.47 |    0.51 |     1    |       -0    |
| salesRank |      -0.02 |      -0.01 |     0.02 |   -0    |   -0.07 |    -0    |        1    |

### Mối quan hệ giữa số trang và giá sách

|             |   no_of_pages |   gbpprice |
|:------------|--------------:|-----------:|
| no_of_pages |          1    |       0.27 |
| gbpprice    |          0.27 |       1    |

### So What?

- Pearson đo mức độ và chiều hướng của mối quan hệ tuyến tính.
- Spearman đánh giá mối quan hệ đơn điệu dựa trên thứ hạng.
- Tương quan không chứng minh quan hệ nhân quả.

**Insight từ dữ liệu:** Cặp biến có tương quan Pearson mạnh nhất là **spine** và **weight**, hệ số tương quan = **0.54** (tương quan thuận).

**Số trang và giá sách:** Hệ số tương quan Pearson giữa số trang và giá sách là **0.27**.

## 2. Phân tích phân loại - số

### Giá theo thể loại

| category     |   Giá trung bình (GBP) |   Giá trung vị (GBP) |   Số lượng sách |
|:-------------|-----------------------:|---------------------:|----------------:|
| artanddesign |               66726.2  |                54.99 |            1038 |
| politics     |                  36.74 |                23.99 |             518 |
| technology   |                  35.46 |                20.99 |             414 |
| medical      |                  30.87 |                26.56 |             405 |
| computing    |                  29.2  |                25.99 |             501 |
| business     |                  22.74 |                15.45 |             493 |
| languages    |                  21.12 |                17.4  |             421 |
| stage        |                  19.36 |                16.16 |             437 |
| socsci       |                  18.21 |                14.52 |             113 |
| education    |                  17.17 |                13.86 |             486 |

### So What?

Bảng này cho phép so sánh giá trung bình, giá trung vị và
số lượng sách giữa các thể loại. Giá trung bình có thể bị
ảnh hưởng bởi những cuốn sách có giá đặc biệt cao hoặc thấp.

**Insight từ dữ liệu:** Trong các thể loại có dữ liệu giá hợp lệ, **artanddesign** có giá trung bình cao nhất là **66726.22 GBP**. Cần lưu ý số lượng sách ở từng thể loại khi so sánh.

## 3. Phân tích phân loại - phân loại

### Bảng chéo giữa thể loại và loại sách

| category      |   Bath Book |   Board Book |   Book |   Calendar |   Diary |   Educational Ca... |   Game |   Hardback |   Hardback (Boxe... |   Hardback (Slip... |   Leather / Fine... |   Merchandise |   Pamphlet / Lea... |   Paperback |   Paperback (Box... |   Plastic-Reinfo... |   Printed Music |   Record Book / ... |   Spiral / Comb ... |   Tong_so_sach |
|:--------------|------------:|-------------:|-------:|-----------:|--------:|--------------------:|-------:|-----------:|--------------------:|--------------------:|--------------------:|--------------:|--------------------:|------------:|--------------------:|--------------------:|----------------:|--------------------:|--------------------:|---------------:|
| artanddesign  |           0 |            0 |      3 |          1 |       1 |                   0 |      0 |        299 |                   0 |                   0 |                   0 |             0 |                   0 |         732 |                   0 |                   0 |               0 |                   0 |                   2 |           1038 |
| childrens     |           2 |           98 |      2 |          0 |       0 |                   0 |      0 |        142 |                   1 |                   0 |                   0 |             0 |                   0 |         274 |                   0 |                   0 |               0 |                   0 |                   2 |            521 |
| politics      |           0 |            0 |      1 |          0 |       0 |                   0 |      0 |        178 |                   0 |                   0 |                   0 |             0 |                   0 |         339 |                   0 |                   0 |               0 |                   0 |                   0 |            518 |
| foodanddrink  |           0 |            0 |      2 |          0 |       0 |                   0 |      0 |        376 |                   0 |                   0 |                   0 |             0 |                   0 |         131 |                   0 |                   1 |               0 |                   0 |                   1 |            511 |
| crime         |           0 |            0 |      0 |          0 |       0 |                   0 |      0 |        137 |                   0 |                   0 |                   0 |             0 |                   0 |         374 |                   0 |                   0 |               0 |                   0 |                   0 |            511 |
| graphicnovels |           0 |            0 |      0 |          0 |       0 |                   0 |      0 |         69 |                   0 |                   0 |                   0 |             0 |                   0 |         439 |                   0 |                   0 |               0 |                   0 |                   0 |            508 |
| biography     |           0 |            0 |      0 |          0 |       0 |                   0 |      0 |        242 |                   0 |                   0 |                   0 |             0 |                   0 |         263 |                   0 |                   0 |               0 |                   0 |                   0 |            505 |
| computing     |           0 |            0 |      0 |          0 |       0 |                   0 |      0 |         87 |                   0 |                   0 |                   0 |             0 |                   0 |         414 |                   0 |                   0 |               0 |                   0 |                   0 |            501 |
| business      |           0 |            0 |      3 |          0 |       0 |                   0 |      0 |        131 |                   0 |                   0 |                   0 |             0 |                   0 |         359 |                   0 |                   0 |               0 |                   0 |                   0 |            493 |
| education     |           0 |            4 |      3 |          0 |       0 |                   0 |      0 |         31 |                   0 |                   0 |                   1 |             0 |                   0 |         445 |                   0 |                   0 |               0 |                   0 |                   2 |            486 |

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
