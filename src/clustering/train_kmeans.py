# Member 2 - Stage 2: Phan cum du lieu sach bang K-Means
# Chay tai thu muc goc project: python src/clustering/train_kmeans.py

from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

ROOT = Path(__file__).resolve().parents[2]
PCA_FILE = ROOT / 'data/stage2/pca/pca_features.csv'
RAW_FILE = ROOT / 'data/cleaned/cleaned_data.csv'
SCHEMA_FILE = ROOT / 'models/pca/feature_schema.json'
PREPROCESS_FILE = ROOT / 'models/pca/preprocessing.joblib'
DATA_DIR = ROOT / 'data/stage2/clustering'
MODEL_DIR = ROOT / 'models/clustering'
CHART_DIR = ROOT / 'visualization/stage2/clustering'
REPORT_FILE = ROOT / 'reports/stage2/clustering_analysis.md'
SEED = 42


def prepare_original(df, features, log_cols):
    # Dung dung cach xu ly feature cua Member 1 de so sanh cong bang
    x = df[features].apply(pd.to_numeric, errors='coerce').copy()
    for col in features:
        if col != 'rating':
            x.loc[x[col] < 0, col] = np.nan
    x.loc[~x['rating'].between(0, 5), 'rating'] = np.nan
    for col in log_cols:
        x[col] = np.log1p(x[col])
    return x


def evaluate_k(x, name):
    # Thu K = 2..8; silhouette lay mau de khong ton qua nhieu thoi gian
    rows = []
    for k in range(2, 9):
        model = KMeans(n_clusters=k, random_state=SEED, n_init=10)
        labels = model.fit_predict(x)
        sil = silhouette_score(x, labels, sample_size=min(1200, len(x)), random_state=SEED)
        rows.append({'method': name, 'k': k, 'inertia': model.inertia_, 'silhouette': sil})
        print(f'{name}: K={k}, silhouette={sil:.4f}, inertia={model.inertia_:.1f}', flush=True)
    return pd.DataFrame(rows)


def main():
    for folder in [DATA_DIR, MODEL_DIR, CHART_DIR, REPORT_FILE.parent]:
        folder.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(RAW_FILE, low_memory=False)
    pca_df = pd.read_csv(PCA_FILE)
    schema = json.loads(SCHEMA_FILE.read_text(encoding='utf-8'))
    preprocessing = joblib.load(PREPROCESS_FILE)
    features = schema['features']

    # Canh theo source_row, khong noi du lieu bang isbn vi co the trung/khuyet
    expected = np.arange(len(df))
    if len(pca_df) != len(df) or not np.array_equal(pca_df['source_row'].to_numpy(), expected):
        raise ValueError('source_row cua PCA khong khop voi du lieu Stage 1')
    x_original = preprocessing.transform(prepare_original(df, features, schema['log1p_features']))
    pc_cols = [c for c in pca_df.columns if c.startswith('PC')]
    x_pca = pca_df[pc_cols].to_numpy()

    # Thu nhieu K va chon K co silhouette cao nhat trong moi cach
    score_original = evaluate_k(x_original, 'Original')
    score_pca = evaluate_k(x_pca, 'PCA')
    scores = pd.concat([score_original, score_pca], ignore_index=True)
    scores.to_csv(DATA_DIR / 'k_evaluation.csv', index=False)
    k_original = int(score_original.loc[score_original['silhouette'].idxmax(), 'k'])
    k_pca = int(score_pca.loc[score_pca['silhouette'].idxmax(), 'k'])

    model_original = KMeans(n_clusters=k_original, random_state=SEED, n_init=10)
    labels_original = model_original.fit_predict(x_original)
    model_pca = KMeans(n_clusters=k_pca, random_state=SEED, n_init=10)
    labels_pca = model_pca.fit_predict(x_pca)
    joblib.dump(model_original, MODEL_DIR / 'kmeans_original.joblib')
    joblib.dump(model_pca, MODEL_DIR / 'kmeans_pca.joblib')

    # Luu nhan cum va chi so dong de Member 5 ghep lai voi dataset
    labels = pd.DataFrame({'source_row': expected, 'Cluster_Original': labels_original,
                           'Cluster_Label': labels_pca})
    labels.to_csv(DATA_DIR / 'cluster_labels.csv', index=False)
    # Ghe nhan vao ban goc; giu nguyen tat ca cac cot
    df_result = df.copy()
    df_result['source_row'] = expected
    df_result['Cluster_Original'] = labels_original
    df_result['Cluster_Label'] = labels_pca
    df_result.to_csv(DATA_DIR / 'clustered_data.csv', index=False)

    # So sanh Elbow va Silhouette tren ca 2 cach
    for metric, filename, ylabel in [('inertia', 'elbow.png', 'Inertia (SSE)'),
                                      ('silhouette', 'silhouette.png', 'Silhouette score')]:
        plt.figure(figsize=(8, 5))
        for method, part in scores.groupby('method'):
            plt.plot(part['k'], part[metric], marker='o', label=method)
        plt.xlabel('So cum K')
        plt.ylabel(ylabel)
        plt.title('K-Means - ' + ('Elbow' if metric == 'inertia' else 'Silhouette'))
        plt.legend()
        plt.grid(alpha=.3)
        plt.tight_layout()
        plt.savefig(CHART_DIR / filename, dpi=150)
        plt.close()

    # Hinh phan cum tren PC1 va PC2
    plt.figure(figsize=(8, 6))
    plt.scatter(x_pca[:, 0], x_pca[:, 1], c=labels_pca, cmap='tab10', s=5, alpha=.45)
    plt.xlabel('PC1')
    plt.ylabel('PC2')
    plt.title(f'K-Means tren du lieu PCA (K={k_pca})')
    plt.tight_layout()
    plt.savefig(CHART_DIR / 'kmeans_pca_scatter.png', dpi=150)
    plt.close()

    # Mo ta tung cum theo trung vi cua cac cot so ban dau
    profile_cols = [c for c in features if c in df_result.columns]
    numeric_profile = df_result[profile_cols].apply(pd.to_numeric, errors='coerce')
    numeric_profile['Cluster_Label'] = labels_pca
    profile = numeric_profile.groupby('Cluster_Label').median(numeric_only=True)
    profile.insert(0, 'so_sach', pd.Series(labels_pca).value_counts().sort_index())
    profile.to_csv(DATA_DIR / 'cluster_profile.csv', index_label='Cluster_Label')

    best_original = float(score_original['silhouette'].max())
    best_pca = float(score_pca['silhouette'].max())
    report = f'''# Báo cáo Member 2 - K-Means (Stage 2)

## 1. Mục tiêu
Em dùng thuật toán K-Means để phân nhóm các bản ghi sách/sản phẩm trong bộ dữ liệu của nhóm. Em thử trên dữ liệu số đã chuẩn hóa và dữ liệu đã giảm chiều bằng PCA của Member 1.

## 2. Dữ liệu và cách làm
- Dữ liệu sạch Stage 1: **{len(df):,} dòng**.
- Dữ liệu ban đầu: **{len(features)} feature số**, dùng lại bộ tiền xử lý của Member 1.
- Dữ liệu PCA: **{len(pc_cols)} thành phần chính**.
- Thử số cụm **K từ 2 đến 8**; sử dụng Elbow (inertia) và Silhouette (lấy mẫu tối đa 1.200 dòng, random_state=42).
- Chọn K có Silhouette cao nhất trong khoảng đã thử, sau đó huấn luyện lại K-Means trên toàn bộ dữ liệu.

## 3. Kết quả

| Dữ liệu | K được chọn | Silhouette (mẫu) |
|---|---:|---:|
| Dữ liệu gốc đã chuẩn hóa | {k_original} | {best_original:.4f} |
| Dữ liệu PCA | {k_pca} | {best_pca:.4f} |

Đây là kết quả theo tiêu chí Silhouette trong khoảng K=2..8, không có nghĩa là số cụm tối ưu cho mọi mục đích. Giá trị inertia giữa hai không gian đặc trưng khác số chiều nên không dùng để kết luận phương pháp nào tốt hơn một cách trực tiếp.

## 4. Nhận xét về các cụm
- Bảng `cluster_profile.csv` thể hiện **trung vị** các đặc trưng số của từng cụm; cột `so_sach` là số bản ghi.
- Nhãn cụm 0, 1, 2... chỉ là mã nhóm, **không phải thứ hạng chất lượng sách**.
- Dataset là dữ liệu sách/sản phẩm, vì vậy đây là **phân cụm sản phẩm**, không phải phân cụm khách hàng.
- Một số đặc trưng có nhiều giá trị thiếu, do đó cần thận trọng khi giải thích đặc điểm từng cụm.

## 5. File bàn giao
- `data/stage2/clustering/k_evaluation.csv`: kết quả thử K.
- `data/stage2/clustering/cluster_labels.csv`: nhãn cụm và `source_row` để ghép lại.
- `data/stage2/clustering/clustered_data.csv`: dữ liệu gốc có thêm nhãn cụm.
- `data/stage2/clustering/cluster_profile.csv`: bảng mô tả các cụm.
- `models/clustering/`: hai model K-Means.
- `visualization/stage2/clustering/`: biểu đồ Elbow, Silhouette, PCA scatter.

## 6. Kết luận
Em đã thử K-Means trên hai cách biểu diễn dữ liệu và tạo cột `Cluster_Label` theo kết quả phân cụm PCA để nhóm sử dụng ở bước tích hợp. Kết quả là phân nhóm dựa trên đặc trưng số; muốn đặt tên cụm theo ý nghĩa thực tế cần xem kỹ bảng profile và chất lượng dữ liệu.
'''
    REPORT_FILE.write_text(report, encoding='utf-8')
    print(f'HOAN THANH: K goc={k_original}, K PCA={k_pca}; silhouette goc={best_original:.4f}, PCA={best_pca:.4f}')


if __name__ == '__main__':
    main()
