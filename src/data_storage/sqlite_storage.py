import pandas as pd
import sqlite3
from pathlib import Path


# ==========================================
# 1. ĐƯỜNG DẪN
# ==========================================

ROOT_DIR = Path(__file__).resolve().parents[2]

DATA_PATH = (
    ROOT_DIR
    / "data"
    / "integrated"
    / "Unified_Integrated_Master_Dataset.csv"
)

SQLITE_DIR = ROOT_DIR / "data" / "sqlite_db"
SQLITE_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = SQLITE_DIR / "integrated_books.db"

TABLE_NAME = "integrated_books"


# ==========================================
# 2. ĐỌC INTEGRATED DATASET
# ==========================================

print("=" * 60)
print("READ INTEGRATED DATASET")
print("=" * 60)

df = pd.read_csv(DATA_PATH, dtype=str)

print(f"Dataset path: {DATA_PATH}")
print(f"Number of records: {len(df)}")
print(f"Number of columns: {len(df.columns)}")


# ==========================================
# 3. KẾT NỐI SQLITE
# ==========================================

print("\n" + "=" * 60)
print("CONNECT SQLITE")
print("=" * 60)

conn = sqlite3.connect(DB_PATH)

print(f"SQLite database: {DB_PATH}")


# ==========================================
# 4. XÓA TABLE CŨ NẾU CÓ
# ==========================================

conn.execute(f"DROP TABLE IF EXISTS {TABLE_NAME}")


# ==========================================
# 5. LƯU DATASET VÀO SQLITE
# ==========================================

print("\n" + "=" * 60)
print("STORE DATA INTO SQLITE")
print("=" * 60)

df.to_sql(
    TABLE_NAME,
    conn,
    if_exists="replace",
    index=False
)

print("All Integrated Dataset records stored in SQLite.")


# ==========================================
# 6. KIỂM TRA SỐ RECORD
# ==========================================

cursor = conn.cursor()

cursor.execute(
    f"SELECT COUNT(*) FROM {TABLE_NAME}"
)

sqlite_count = cursor.fetchone()[0]

print("\n" + "=" * 60)
print("VERIFY SQLITE")
print("=" * 60)

print(f"Dataset records : {len(df)}")
print(f"SQLite records  : {sqlite_count}")

if sqlite_count == len(df):
    print("Verification successful!")
else:
    print("Record count does not match.")


# ==========================================
# 7. KIỂM TRA DỮ LIỆU MẪU
# ==========================================

print("\n" + "=" * 60)
print("SAMPLE RECORD")
print("=" * 60)

sample = pd.read_sql_query(
    f"SELECT * FROM {TABLE_NAME} LIMIT 1",
    conn
)

print(sample.to_string())


# ==========================================
# 8. ĐÓNG DATABASE
# ==========================================

conn.close()

print("\n" + "=" * 60)
print("SQLITE DATABASE COMPLETED")
print("=" * 60)
