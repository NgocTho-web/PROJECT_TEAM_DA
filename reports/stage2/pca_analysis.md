# BÁO CÁO STAGE 2 - MEMBER 1: PCA

## 1. Mục tiêu
Em thực hiện giảm chiều dữ liệu bằng PCA để giữ lại những thông tin quan trọng, đồng thời tạo dữ liệu đầu vào cho thành viên làm K-Means.

## 2. Dữ liệu sử dụng
- File đầu vào: `data/cleaned/cleaned_data.csv` của Stage 1.
- Dữ liệu có 12.133 dòng và 42 cột.
- Em chọn 12 cột số: `gbpprice`, `discount`, `height`, `width`, `spine`, `weight`, `salesRank`, `original_price`, `discount_price`, `discount_percentage`, `rating`, `rating_count`.
- Không đưa các cột mã định danh và văn bản trực tiếp vào PCA.

## 3. Các bước thực hiện
1. Đọc dữ liệu bằng pandas và lấy các cột cần thiết.
2. Chuyển dữ liệu sang dạng số; giá trị âm không hợp lệ và rating ngoài khoảng 0–5 được xem là thiếu.
3. Dùng `log1p` với một số cột giá, xếp hạng, số lượng đánh giá để giảm độ lệch.
4. Điền giá trị thiếu bằng trung vị (`SimpleImputer`).
5. Chuẩn hóa dữ liệu bằng `StandardScaler`.
6. Chạy PCA và xem `explained_variance_ratio_`, phương sai tích lũy.
7. Chọn số thành phần đủ giữ ít nhất 90% phương sai, vẽ biểu đồ và lưu kết quả.

## 4. Kết quả
- Số feature ban đầu: **12**.
- Số thành phần PCA được chọn: **9**.
- Tổng phương sai được giữ lại: **92,77%**.
- PC1 giải thích khoảng **20,15%**, PC2 khoảng **18,41%** phương sai.
- Biểu đồ `cumulative_variance.png` cho thấy khi dùng 9 thành phần đã đạt mục tiêu 90%.
- Biểu đồ `pca_scatter_2d.png` thể hiện dữ liệu theo hai trục PC1 và PC2 để dễ quan sát.

## 5. Nhận xét
Sau khi áp dụng PCA, dữ liệu giảm từ 12 feature xuống 9 thành phần nhưng vẫn giữ hơn 90% phương sai. Như vậy có thể sử dụng kết quả PCA để thử phân cụm K-Means và so sánh với dữ liệu trước PCA.

Lưu ý: dữ liệu hiện tại chủ yếu là thông tin sách/sản phẩm, không phải dữ liệu giao dịch của từng khách hàng. Các cột giá cũng có thể đến từ nguồn hoặc đơn vị tiền khác nhau nên không được hiểu là cùng một loại giá.

## 6. Bàn giao cho Member 2
- `data/stage2/pca/pca_features.csv`: dữ liệu PCA gồm `source_row`, `PC1` đến `PC9`.
- `models/pca/preprocessing.joblib`: bộ điền dữ liệu thiếu và chuẩn hóa.
- `models/pca/pca_model.joblib`: mô hình PCA.
- `models/pca/feature_schema.json`: danh sách và thứ tự feature, các cột cần `log1p`.
- `data/stage2/pca/row_mapping.csv`: ghép kết quả PCA về đúng dòng dữ liệu gốc.

Member 2 có thể dùng `pca_features.csv` để chạy K-Means, thử nhiều giá trị K, dùng Elbow và Silhouette để đánh giá.
