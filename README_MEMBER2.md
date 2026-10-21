# Member 2 - K-Means (Stage 2)

Bài này dùng kết quả PCA của Member 1 và file dữ liệu sạch từ Stage 1 để phân cụm sách/sản phẩm.

## Cách chạy

Mở terminal ở thư mục gốc `PROJECT_TEAM_DA`:

```bash
pip install numpy pandas scikit-learn matplotlib joblib
python src/clustering/train_kmeans.py
```

Cần có sẵn các file:
- `data/cleaned/cleaned_data.csv` (Stage 1)
- `data/stage2/pca/pca_features.csv` (Member 1)
- `models/pca/feature_schema.json` (Member 1)
- `models/pca/preprocessing.joblib` (Member 1)

Chương trình tự lưu model, kết quả phân cụm, biểu đồ và báo cáo. Không cần chép lại dữ liệu của Stage 1 hoặc Member 1 vào bài Member 2.

## Nộp GitHub

Đưa các thư mục `src/clustering`, `models/clustering`, `data/stage2/clustering`, `visualization/stage2/clustering`, `reports/stage2` vào đúng vị trí của repository. Nên tạo branch riêng trước khi nộp.

**Kết quả đã chạy:** Original chọn K=3 (Silhouette 0.2470), PCA chọn K=2 (Silhouette 0.7451 trên mẫu). Cụm PCA khá lệch kích thước (12.012 và 121), xem phần lưu ý trong báo cáo.
