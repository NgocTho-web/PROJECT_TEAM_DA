import pandas as pd
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.models import (
    PointStruct,
    VectorParams,
    Distance
)

from sentence_transformers import SentenceTransformer

# 1. PROJECT PATH

ROOT_DIR = Path(__file__).resolve().parents[2]

DATA_PATH = (
    ROOT_DIR
    / "data"
    / "integrated"
    / "Unified_Integrated_Master_Dataset.csv"
)

QDRANT_PATH = (
    ROOT_DIR
    / "data"
    / "qdrant_db"
)

COLLECTION_NAME = "integrated_books"

# 2. READ INTEGRATED DATASET
print("READ INTEGRATED DATASET")

df = pd.read_csv(
    DATA_PATH,
    dtype=str
)

print("Dataset path:", DATA_PATH)
print("Number of records:", len(df))
print("Number of columns:", len(df.columns))

print("\nColumns:")
print(df.columns.tolist())

# 3. CONNECT TO QDRANT
print("CONNECT QDRANT")

client = QdrantClient(
    path=str(QDRANT_PATH)
)

print("Connected to Qdrant.")
print("Qdrant path:", QDRANT_PATH)

# 4. LOAD EMBEDDING MODEL
print("LOAD EMBEDDING MODEL")

model = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

print("Embedding model loaded.")

# 5. CREATE TEXT FOR EMBEDDING
print("CREATE EMBEDDING TEXT")

def create_embedding_text(row):

    values = []

    for column in df.columns:

        value = row[column]

        if pd.notna(value):

            values.append(
                f"{column}: {value}"
            )

    return " | ".join(values)


df["embedding_text"] = df.apply(
    create_embedding_text,
    axis=1
)

print("Embedding text created.")

print("\nExample:")
print(df["embedding_text"].iloc[0][:500])

# 6. CREATE EMBEDDINGS
print("CREATE EMBEDDINGS")
texts = df["embedding_text"].tolist()

embeddings = model.encode(
    texts,
    show_progress_bar=True
)

vector_size = len(embeddings[0])

print("Number of vectors:", len(embeddings))
print("Vector dimension:", vector_size)

# 7. CREATE QDRANT COLLECTION
print("CREATE QDRANT COLLECTION")

if client.collection_exists(COLLECTION_NAME):

    print(
        f"Collection '{COLLECTION_NAME}' already exists."
    )

else:

    client.create_collection(
        collection_name=COLLECTION_NAME,

        vectors_config=VectorParams(
            size=vector_size,
            distance=Distance.COSINE
        )
    )

    print(
        f"Collection '{COLLECTION_NAME}' created."
    )

# 8. PREPARE QDRANT POINTS
print("PREPARE QDRANT POINTS")
points = []


for index, row in df.iterrows():

    payload = {}

    for column in df.columns:

        # Không lưu cột phụ embedding_text
        if column == "embedding_text":
            continue

        value = row[column]

        if pd.isna(value):

            payload[column] = None

        else:

            payload[column] = value


    point = PointStruct(

        id=index + 1,

        vector=embeddings[index].tolist(),

        payload=payload
    )

    points.append(point)


print("Number of points:", len(points))

# 9. INGEST DATA INTO QDRANT
print("INGEST DATA")

client.upsert(

    collection_name=COLLECTION_NAME,

    points=points
)

print(
    "All Integrated Dataset records "
    "have been stored in Qdrant."
)

# 10. VERIFY NUMBER OF RECORDS
print("VERIFY QDRANT")

count_result = client.count(

    collection_name=COLLECTION_NAME,

    exact=True
)


print(
    "Records in Integrated Dataset:",
    len(df)
)

print(
    "Records in Qdrant:",
    count_result.count
)

# 11. VERIFY CONTENT
print("VERIFY CONTENT")

sample = client.retrieve(

    collection_name=COLLECTION_NAME,

    ids=[1],

    with_payload=True,

    with_vectors=False
)


if sample:

    print("First record stored in Qdrant:")

    print(sample[0].payload)

else:

    print("No record found.")

print("QDRANT DATABASE COMPLETED")