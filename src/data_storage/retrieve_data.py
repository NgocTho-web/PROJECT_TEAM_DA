import pandas as pd
import sqlite3
from pathlib import Path

from qdrant_client import QdrantClient


# ==========================================
# 1. ĐƯỜNG DẪN
# ==========================================

ROOT_DIR = Path(__file__).resolve().parents[2]

RETRIEVED_DIR = ROOT_DIR / "data" / "retrieved"
RETRIEVED_DIR.mkdir(parents=True, exist_ok=True)


# =========================================================
# PART 1 - RETRIEVE DATA FROM QDRANT
# =========================================================

print("=" * 60)
print("RETRIEVE DATA FROM QDRANT")
print("=" * 60)


QDRANT_PATH = ROOT_DIR / "data" / "qdrant_db"

client = QdrantClient(
    path=str(QDRANT_PATH)
)

COLLECTION_NAME = "integrated_books"


# Lấy toàn bộ records
records = []

offset = None

while True:

    points, offset = client.scroll(
        collection_name=COLLECTION_NAME,
        limit=1000,
        offset=offset,
        with_payload=True,
        with_vectors=False
    )

    for point in points:
        records.append(point.payload)

    if offset is None:
        break


qdrant_df = pd.DataFrame(records)


print(f"Qdrant records retrieved: {len(qdrant_df)}")
print(f"Qdrant columns retrieved: {len(qdrant_df.columns)}")


# Lưu dataset lấy từ Qdrant
qdrant_output = RETRIEVED_DIR / "qdrant_retrieved.csv"

qdrant_df.to_csv(
    qdrant_output,
    index=False
)

print(f"Saved to: {qdrant_output}")


client.close()


# =========================================================
# PART 2 - RETRIEVE DATA FROM SQLITE
# =========================================================

print("\n" + "=" * 60)
print("RETRIEVE DATA FROM SQLITE")
print("=" * 60)


SQLITE_PATH = (
    ROOT_DIR
    / "data"
    / "sqlite_db"
    / "integrated_books.db"
)

TABLE_NAME = "integrated_books"


conn = sqlite3.connect(SQLITE_PATH)


# Lấy toàn bộ dữ liệu
sqlite_df = pd.read_sql_query(
    f"SELECT * FROM {TABLE_NAME}",
    conn
)


print(f"SQLite records retrieved: {len(sqlite_df)}")
print(f"SQLite columns retrieved: {len(sqlite_df.columns)}")


# Lưu dataset lấy từ SQLite
sqlite_output = RETRIEVED_DIR / "sqlite_retrieved.csv"

sqlite_df.to_csv(
    sqlite_output,
    index=False
)

print(f"Saved to: {sqlite_output}")


conn.close()


# =========================================================
# PART 3 - FINAL VERIFICATION
# =========================================================

print("\n" + "=" * 60)
print("FINAL VERIFICATION")
print("=" * 60)

print(f"Qdrant retrieved : {len(qdrant_df)} records")
print(f"SQLite retrieved : {len(sqlite_df)} records")


if len(qdrant_df) == len(sqlite_df):
    print("Both databases returned the same number of records.")
else:
    print("Record counts are different.")


print("\n" + "=" * 60)
print("RETRIEVAL COMPLETED")
print("=" * 60)
