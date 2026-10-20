# Báo cáo Member 2 - K-Means (Stage 2)

## 1. Mục tiêu
Em dùng thuật toán K-Means để phân nhóm các bản ghi sách/sản phẩm trong bộ dữ liệu của nhóm. Em thử trên dữ liệu số đã chuẩn hóa và dữ liệu đã giảm chiều bằng PCA của Member 1.

## 2. Dữ liệu và cách làm
- Dữ liệu sạch Stage 1: **12,133 dòng**.
- Dữ liệu ban đầu: **12 feature số**, dùng lại bộ tiền xử lý của Member 1.
- Dữ liệu PCA: **9 thành phần chính**.
- Thử số cụm **K từ 2 đến 8**; sử dụng Elbow (inertia) và Silhouette (lấy mẫu tối đa 1.200 dòng, random_state=42).
- Chọn K có Silhouette cao nhất trong khoảng đã thử, sau đó huấn luyện lại K-Means trên toàn bộ dữ liệu.

## 3. Kết quả

| Dữ liệu | K được chọn | Silhouette (mẫu) |
|---|---:|---:|
| Dữ liệu gốc đã chuẩn hóa | 3 | 0.2470 |
| Dữ liệu PCA | 2 | 0.7451 |

Đây là kết quả theo tiêu chí Silhouette trong khoảng K=2..8, không có nghĩa là số cụm tối ưu cho mọi mục đích. Giá trị inertia giữa hai không gian đặc trưng khác số chiều nên không dùng để kết luận phương pháp nào tốt hơn một cách trực tiếp.

## 4. Nhận xét về các cụm
- Bảng `cluster_profile.csv` thể hiện **trung vị** các đặc trưng số của từng cụm; cột `so_sach` là số bản ghi.
- Nhãn cụm 0, 1, 2... chỉ là mã nhóm, **không phải thứ hạng chất lượng sách**.
- Dataset là dữ liệu sách/sản phẩm, vì vậy đây là **phân cụm sản phẩm**, không phải phân cụm khách hàng.
- Một số đặc trưng có nhiều giá trị thiếu, do đó cần thận trọng khi giải thích đặc điểm từng cụm.

### Lưu ý khi giải thích kết quả

Với K=2 trên dữ liệu PCA, cụm 0 có **12.012** bản ghi và cụm 1 có **121** bản ghi. Sự chênh lệch này khá lớn: Silhouette cao có thể xuất hiện do một nhóm nhỏ có đặc trưng khác biệt, **không chứng minh chắc chắn phân cụm tốt cho mục đích kinh doanh**. Nếu cần các nhóm cân đối và dễ diễn giải, nhóm nên xem thêm kết quả K=3 hoặc K=4 trong `k_evaluation.csv` và kiểm tra biểu đồ.

## 5. File bàn giao
- `data/stage2/clustering/k_evaluation.csv`: kết quả thử K.
- `data/stage2/clustering/cluster_labels.csv`: nhãn cụm và `source_row` để ghép lại.
- `data/stage2/clustering/clustered_data.csv`: dữ liệu gốc có thêm nhãn cụm.
- `data/stage2/clustering/cluster_profile.csv`: bảng mô tả các cụm.
- `models/clustering/`: hai model K-Means.
- `visualization/stage2/clustering/`: biểu đồ Elbow, Silhouette, PCA scatter.

## 6. Kết luận
Em đã thử K-Means trên hai cách biểu diễn dữ liệu và tạo cột `Cluster_Label` theo kết quả phân cụm PCA để nhóm sử dụng ở bước tích hợp. Kết quả là phân nhóm dựa trên đặc trưng số; muốn đặt tên cụm theo ý nghĩa thực tế cần xem kỹ bảng profile và chất lượng dữ liệu.
