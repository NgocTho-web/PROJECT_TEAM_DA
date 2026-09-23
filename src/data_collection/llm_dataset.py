import pandas as pd
import ollama
from tqdm import tqdm


# ==========================================
# 1. ĐỌC FILE DYNAMIC_DATASET
# ==========================================

df = pd.read_csv("D:/PROJECT_TEAM_DA/PROJECT_TEAM_DA/data/raw/dynamic_dataset.csv")

df = df.head(20)
# ==========================================
# 2. HÀM GỌI OLLAMA
# ==========================================

def generate_book_content(book_name, author, publisher):

    prompt = f"""
Bạn là chuyên gia viết nội dung về sách.

Thông tin cuốn sách:

Tên sách: {book_name}
Tác giả: {author}
Nhà xuất bản: {publisher}

Hãy tạo nội dung gồm 4 phần:

1. Mô tả sách: khoảng 50-80 từ
2. Review: khoảng 40-60 từ
3. Thể loại: chọn một thể loại phù hợp
4. Đối tượng độc giả: mô tả nhóm độc giả phù hợp

Trả kết quả theo đúng định dạng:

Mô tả: ...
Review: ...
Thể loại: ...
Đối tượng độc giả: ...
"""

    response = ollama.chat(
        model="llama3.2",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]


# ==========================================
# 3. GỌI OLLAMA CHO TỪNG CUỐN SÁCH
# ==========================================

llm_content = []

for _, row in tqdm(
    df.iterrows(),
    total=len(df),
    desc="Đang tạo dữ liệu bằng Ollama"
):

    content = generate_book_content(
        row["Tên sách"],
        row["Tác giả"],
        row["Nhà xuất bản"]
    )

    llm_content.append(content)


# ==========================================
# 4. THÊM CỘT DO LLM SINH RA
# ==========================================

df["LLM Content"] = llm_content


# ==========================================
# 5. LƯU FILE
# ==========================================

df.to_csv(
    r"D:/PROJECT_TEAM_DA/PROJECT_TEAM_DA/data/raw/llm_dataset.csv",
    index=False,
    encoding="utf-8-sig"
)


print("\n================================")
print("ĐÃ TẠO XONG llm_dataset.csv")
print("================================")

print("\nCác cột:")
print(df.columns.tolist())

print("\n5 dòng đầu:")
print(df.head())