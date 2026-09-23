import pandas as pd
import numpy as np

# Số lượng sách
n = 1000

# Danh sách sách
books = [
    "Đắc Nhân Tâm",
    "Nhà Giả Kim",
    "Tuổi Trẻ Đáng Giá Bao Nhiêu",
    "Muôn Kiếp Nhân Sinh",
    "Cây Cam Ngọt Của Tôi",
    "Hoàng Tử Bé",
    "Không Gia Đình",
    "Dế Mèn Phiêu Lưu Ký",
    "Harry Potter",
    "Những Người Khốn Khổ",
    "Sherlock Holmes",
    "Atomic Habits",
    "Deep Work",
    "The Psychology of Money",
    "Think and Grow Rich"
]

authors = [
    "Nguyễn Nhật Ánh",
    "Nguyễn Ngọc Tư",
    "Tony Buổi Sáng",
    "Paulo Coelho",
    "Dale Carnegie",
    "Robin Sharma",
    "James Clear",
    "J.K. Rowling",
    "Victor Hugo",
    "Antoine de Saint-Exupéry"
]

publishers = [
    "NXB Trẻ",
    "NXB Kim Đồng",
    "NXB Văn Học",
    "NXB Tổng Hợp TP.HCM",
    "NXB Phụ Nữ Việt Nam",
    "NXB Lao Động",
    "NXB Thế Giới"
]

# Tạo DataFrame
df = pd.DataFrame({
    "ID": range(1, n + 1),

    "Tên sách": np.random.choice(
        books, n
    ),

    "Tác giả": np.random.choice(
        authors, n
    ),

    "Nhà xuất bản": np.random.choice(
        publishers, n
    ),

    # Giá gốc: 30.000 - 500.000
    "Giá gốc": np.random.randint(
        30_000, 500_001, n
    ),

    # Giảm từ 0% - 50%
    "Phần trăm giảm": np.random.randint(
        0, 51, n
    ),

    # Đánh giá từ 1 - 5
    "Đánh giá": np.round(
        np.random.uniform(3, 5, n), 1
    ),

    # Số lượt đánh giá
    "Số lượt đánh giá": np.random.randint(
        0, 20_001, n
    )
})

# Tính số tiền giảm
df["Giảm giá"] = (
    df["Giá gốc"] *
    df["Phần trăm giảm"] / 100
).round(0)

# Tính giá bán
df["Giá"] = (
    df["Giá gốc"] -
    df["Giảm giá"]
).round(0)

# Sắp xếp cột
df = df[
    [
        "ID",
        "Tên sách",
        "Tác giả",
        "Nhà xuất bản",
        "Giá",
        "Giá gốc",
        "Giảm giá",
        "Phần trăm giảm",
        "Đánh giá",
        "Số lượt đánh giá"
    ]
]

df.to_csv(
    r"D:/PROJECT_TEAM_DA/PROJECT_TEAM_DA/data/raw/dynamic_dataset.csv",
    index=False,
    encoding="utf-8-sig"
)