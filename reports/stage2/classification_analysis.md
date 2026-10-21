# Classification Analysis - Member 4

- **Dataset:** `cleaned_data.csv`
- **Số dòng dùng được:** 12133
- **Target:** `category`
- **Số lớp:** 28
- **Feature đầu vào:** gbpprice, discount, no_of_pages, height, width, spine, weight, salesRank, original_price, discount_price, discount_percentage, rating, rating_count, type, language, published_country
- **Tỷ lệ lớp nhỏ nhất/lớn nhất:** 0.109
- **Xử lý mất cân bằng:** class_weight=balanced

## 1. Phương pháp
Dữ liệu được chia thành 80% train và 20% test với `stratify=y`, `random_state=42`. Các feature số được điền thiếu bằng median và chuẩn hóa StandardScaler; feature phân loại được điền thiếu bằng mode và mã hóa OneHotEncoder. Các bước tiền xử lý được đặt trong Pipeline để chỉ fit trên tập train.

## 2. Kết quả so sánh
| model               |   accuracy |   precision_macro |   recall_macro |   f1_macro |   f1_weighted |
|:--------------------|-----------:|------------------:|---------------:|-----------:|--------------:|
| Decision Tree       |     0.2752 |            0.2687 |         0.2433 |     0.2508 |        0.2922 |
| Logistic Regression |     0.2901 |            0.2678 |         0.2536 |     0.2411 |        0.2818 |

## 3. Mô hình được chọn
Mô hình tốt nhất theo **Macro F1-score** (dùng Accuracy làm tiêu chí phụ khi hòa) là **Decision Tree**. Model và preprocessing được lưu tại `models/classification/best_model.joblib`.

## 4. Biểu đồ
- `visualization/stage2/classification/confusion_matrix_logistic_regression.png`
- `visualization/stage2/classification/confusion_matrix_decision_tree.png`

## 5. Hạn chế và lưu ý
- Target `category` được chọn làm bài toán phân loại nhiều lớp; cần xác nhận đây là mục tiêu phù hợp với câu hỏi kinh doanh của nhóm.
- Một số cột mô tả văn bản, ID, tên sách và các cột tiếng Việt bị lặp/không đồng nhất không được đưa vào mô hình.
- Kết quả chỉ phản ánh tập test của lần chia dữ liệu này; không khẳng định quan hệ nhân quả.
- Trước khi triển khai, cần kiểm thử dữ liệu mới có đúng các feature đầu vào được ghi trong `model_metadata.json`.

## 6. Bàn giao cho Member 5
Nạp `models/classification/best_model.joblib` bằng `joblib.load(...)`. Đây là Pipeline hoàn chỉnh; gọi `predict()` trực tiếp trên DataFrame chứa các cột trong `input_features` của `model_metadata.json`.