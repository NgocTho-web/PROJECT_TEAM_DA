import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv("data/blackwell_shop_cleaned.csv")

df["no_of_pages"] = pd.to_numeric(
    df["no_of_pages"],
    errors="coerce"
)

# ==============================
# 1. Biểu đồ nhiệt tương quan
# ==============================

plt.figure(figsize=(10, 7))

sns.heatmap(
    df[
        [
            "gbpprice",
            "discount",
            "height",
            "width",
            "spine",
            "weight",
            "salesRank"
        ]
    ].corr(),
    annot=True,
    cmap="coolwarm"
)

plt.title("Ma trận tương quan giữa các biến số")
plt.xlabel("Các biến số")
plt.ylabel("Các biến số")
plt.tight_layout()

plt.savefig(
    "visualization/01_correlation_heatmap.png"
)

plt.show()


# ==============================
# 2. Biểu đồ phân tán
# ==============================

plt.figure(figsize=(8, 5))

sns.scatterplot(
    data=df,
    x="no_of_pages",
    y="gbpprice"
)

plt.title("Mối quan hệ giữa số trang và giá")
plt.xlabel("Số trang")
plt.ylabel("Giá (GBP)")
plt.tight_layout()

plt.savefig(
    "visualization/02_scatter_plot.png"
)

plt.show()


# ==============================
# 3. Biểu đồ cột nhóm
# ==============================

gia_theo_the_loai = (
    df.groupby("category")["gbpprice"]
    .mean()
    .sort_values(ascending=False)
    .head(10)
)

gia_theo_the_loai.plot(
    kind="bar",
    figsize=(9, 5)
)

plt.title("Giá trung bình theo thể loại")
plt.xlabel("Thể loại")
plt.ylabel("Giá trung bình (GBP)")
plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig(
    "visualization/03_grouped_bar_chart.png"
)

plt.show()


# ==============================
# 4. Biểu đồ hộp theo nhóm
# ==============================

the_loai_top = (
    df["category"]
    .value_counts()
    .head(10)
    .index
)

plt.figure(figsize=(10, 5))

sns.boxplot(
    data=df[df["category"].isin(the_loai_top)],
    x="category",
    y="gbpprice"
)

plt.title("Phân bố giá theo thể loại")
plt.xlabel("Thể loại")
plt.ylabel("Giá (GBP)")
plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig(
    "visualization/04_grouped_box_plot.png"
)

plt.show()


# ==============================
# 5. Biểu đồ cột chồng
# ==============================

bang = pd.crosstab(
    df["category"],
    df["type"]
).head(10)

bang.plot(
    kind="bar",
    stacked=True,
    figsize=(10, 5)
)

plt.title("Phân bố loại sách theo thể loại")
plt.xlabel("Thể loại")
plt.ylabel("Số lượng sách")
plt.legend(title="Loại sách")
plt.tight_layout()

plt.savefig(
    "visualization/05_stacked_bar_chart.png"
)

plt.show()


# ==============================
# 6. Histogram + KDE
# ==============================

plt.figure(figsize=(8, 5))

sns.histplot(
    df["gbpprice"],
    kde=True
)

plt.title("Phân bố giá sách")
plt.xlabel("Giá (GBP)")
plt.ylabel("Tần số")
plt.tight_layout()

plt.savefig(
    "visualization/06_histogram_kde.png"
)

plt.show()


# ==============================
# 7. Biểu đồ hộp
# ==============================

plt.figure(figsize=(7, 5))

sns.boxplot(
    x=df["gbpprice"]
)

plt.title("Biểu đồ hộp của giá sách")
plt.xlabel("Giá (GBP)")
plt.ylabel("Giá trị")
plt.tight_layout()

plt.savefig(
    "visualization/07_box_plot.png"
)

plt.show()


# ==============================
# 8. Biểu đồ cột nhà xuất bản
# ==============================

nha_xuat_ban = (
    df["publisher"]
    .value_counts()
    .head(10)
)

nha_xuat_ban.plot(
    kind="bar",
    figsize=(9, 5)
)

plt.title("10 nhà xuất bản có nhiều sách nhất")
plt.xlabel("Nhà xuất bản")
plt.ylabel("Số lượng sách")
plt.xticks(rotation=45)
plt.tight_layout()

plt.savefig(
    "visualization/08_bar_chart_publishers.png"
)

plt.show()


# ==============================
# 9. Biểu đồ tròn
# ==============================

loai_sach = (
    df["type"]
    .value_counts()
    .head(5)
)

loai_sach.plot(
    kind="pie",
    autopct="%1.1f%%",
    figsize=(7, 7)
)

plt.title("5 loại sách phổ biến nhất")
plt.xlabel("")
plt.ylabel("")
plt.tight_layout()

plt.savefig(
    "visualization/09_pie_chart_types.png"
)

plt.show()