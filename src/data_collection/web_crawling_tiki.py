import requests
import json
import pandas as pd

url = "https://tiki.vn/api/personalish/v1/blocks/listings"

params = {
    "limit": 10,
    "sort": "top_seller",
    "page": 1,
    "urlKey": "nha-sach-tiki",
    "category": 8322
}

headers = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/152.0.0.0 Safari/537.36",
    "Referer": "https://tiki.vn/nha-sach-tiki/c8322"
}

all_products = []

for page in range(1, 50):

    params["page"] = page

    response = requests.get(
        url,
        params=params,
        headers=headers,
        timeout=15
    )

    # Chuyển JSON thành Python dictionary
    data = response.json()

    print(data.keys())

    data = response.json()

    for item in data["data"]:

        product = {
            "ID": item.get("id"),
            "Tên sản phẩm": item.get("name"),
            "Thương hiệu": item.get("brand_name"),
            "Giá": item.get("price"),
            "Giá gốc": item.get("original_price"),
            "Giảm giá": item.get("discount"),
            "Phần trăm giảm": item.get("discount_rate"),
            "Đánh giá": item.get("rating_average"),
            "Số lượt đánh giá": item.get("review_count"),
        }

        all_products.append(product)

print("Tổng số sản phẩm:", len(all_products))

df = pd.DataFrame(all_products)

df.to_csv(
    r"D:/PROJECT_TEAM_DA/PROJECT_TEAM_DA/data/raw/web_crawling_tiki.csv",
    index=False,
    encoding="utf-8-sig"
)

print(df.head())