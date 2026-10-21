# KIM ANH - MODEL INTEGRATION & STREAMLIT

**Người thực hiện:** Dương Thị Kim Anh  
**GitHub:** dtkanh2k6  
**Branch:** kimanh-model-integration

## 1. Nhiệm vụ

Tích hợp các mô hình Machine Learning của nhóm thành một hệ thống phân tích và dự đoán sách, đồng thời xây dựng giao diện bằng Streamlit.

## 2. Các chức năng

- Dự đoán thể loại sách bằng mô hình Classification.
- Dự đoán giá sách bằng mô hình Regression (GBP).
- Phân cụm sách bằng K-Means trên dữ liệu đặc trưng gốc.
- Phân cụm sách bằng K-Means kết hợp PCA.
- Dự đoán tổng hợp kết quả Classification, Regression và K-Means.

## 3. Các file chính

- `src/integration/predict.py`: Tích hợp và gọi các mô hình dự đoán.
- `app/app.py`: Giao diện chính của ứng dụng Streamlit.
- `app/components.py`: Các thành phần hỗ trợ giao diện.
- `app/utils.py`: Các hàm tiện ích.

## 4. Chạy ứng dụng

Tại thư mục gốc của project, cài đặt các thư viện cần thiết và chạy:

```bash
python -m streamlit run app/app.py
```

Truy cập địa chỉ `http://localhost:8501` để sử dụng.

## 5. Kết quả kiểm thử

Đã thực hiện kiểm thử chức năng trên dữ liệu sách mẫu.

- Classification: chạy thành công.
- Regression: chạy thành công.
- K-Means không PCA: chạy thành công.
- K-Means có PCA: chạy thành công.
- Dự đoán tổng hợp: chạy thành công.

**Lưu ý:** Kết quả kiểm thử xác nhận các chức năng chạy được, không thay thế việc đánh giá độ chính xác của mô hình.