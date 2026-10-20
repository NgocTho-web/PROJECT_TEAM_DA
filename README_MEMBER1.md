# Member 1 - PCA (Stage 2)

Bài này dùng file dữ liệu sạch của Stage 1 tại `data/cleaned/cleaned_data.csv`.

## Cách chạy
Mở terminal tại thư mục gốc repository, chạy:

```bash
pip install pandas numpy scikit-learn matplotlib joblib
python src/pca/train_pca.py
```

Code sẽ tạo dữ liệu PCA, model và 2 biểu đồ. Kết quả và nhận xét nằm trong `reports/stage2/pca_analysis.md`.

## Nộp GitHub
Copy các thư mục `src/pca`, `data/stage2/pca`, `models/pca`, `visualization/stage2/pca`, `reports/stage2` vào repo đúng vị trí.
Không cần chép đè `data/cleaned/cleaned_data.csv` vì nhóm đã có file từ Stage 1.
