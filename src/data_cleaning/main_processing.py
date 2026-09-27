from pathlib import Path
import pandas as pd
from cleaner import clean_data
from encoder import encode_features

# ==========================================
# 1. KHAI BÁO ĐƯỜNG DẪN (Giống Member 3)
# ==========================================
ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_PATH = (
    ROOT_DIR
    / "data"
    / "integrated"
    / "Unified_Integrated_Master_Dataset.csv"
)

print("=" * 60)
print("MEMBER 4: TIỀN XỬ LÝ VÀ LÀM SẠCH DỮ LIỆU")
print("=" * 60)

# ==========================================
# 2. ĐỌC DỮ LIỆU TỪ MEMBER 3
# ==========================================
try:
    df = pd.read_csv(DATA_PATH)
    print(f"--> Đã tải dữ liệu thành công từ: {DATA_PATH}")
except Exception:
    print(
        "--> Chưa tìm thấy file chính, đang dùng dữ liệu thử nghiệm..."
    )
    df = pd.DataFrame(
        {
            "Title": ["Sách A", "Sách B", "Sách A", "Sách C"],
            "Price": [100000, "ERROR", 100000, 150000],
            "Category": ["Fiction", "Non-Fiction", "Fiction", "UNKNOWN"],
        }
    )

# ==========================================
# 3. TIẾN HÀNH XỬ LÝ DỮ LIỆU
# ==========================================
print("\n1. Đang làm sạch dữ liệu...")
df_clean = clean_data(df)

print("2. Đang thực hiện One-Hot Encoding...")
df_processed = encode_features(df_clean)

# ==========================================
# 4. HIỂN THỊ VÀ LƯU KẾT QUẢ
# ==========================================
print("\n--> Bảng dữ liệu hoàn chỉnh sau khi xử lý:")
print(df_processed.head())

OUTPUT_PATH = ROOT_DIR / "data" / "cleaned_data.csv"
OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
df_processed.to_csv(OUTPUT_PATH, index=False)

print("\n" + "=" * 60)
print(f"ĐÃ LƯU FILE KẾT QUẢ TẠI: {OUTPUT_PATH}")
print("=" * 60)