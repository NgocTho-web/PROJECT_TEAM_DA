
from pathlib import Path
import sys

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.integration.predict import (
    predict_classification,
    predict_regression,
    predict_clustering,
    predict_all,
)

st.set_page_config(
    page_title="Hệ thống phân tích sách",
    page_icon="📚",
    layout="wide",
)

st.title("📚 HỆ THỐNG PHÂN TÍCH VÀ DỰ ĐOÁN SÁCH")
st.caption("Ứng dụng Machine Learning - Đồ án phân tích dữ liệu")

DATA_PATH = ROOT / "data" / "cleaned" / "cleaned_data.csv"

@st.cache_data
def load_data():
    return pd.read_csv(DATA_PATH)

st.sidebar.title("📚 MENU")
page = st.sidebar.radio(
    "Chọn chức năng",
    [
        "Trang chủ",
        "Dự đoán thể loại",
        "Dự đoán giá sách",
        "Phân cụm K-Means",
        "Dự đoán tổng hợp",
    ],
)

st.sidebar.divider()
st.sidebar.caption("Hệ thống tích hợp Classification, Regression và K-Means")

if not DATA_PATH.exists():
    st.error("Không tìm thấy dữ liệu cleaned_data.csv")
    st.stop()

try:
    df = load_data()
except Exception as e:
    st.error(f"Không đọc được dữ liệu: {e}")
    st.stop()

if page == "Trang chủ":
    st.subheader("🏠 Tổng quan hệ thống")
    st.write(
        "Hệ thống ứng dụng Machine Learning để phân tích, "
        "dự đoán thể loại, giá bán và phân cụm sách."
    )

    a, b, c = st.columns(3)
    a.metric("Số bản ghi", f"{len(df):,}")
    b.metric("Số thuộc tính", len(df.columns))
    c.metric("Số mô hình chính", 3)

    st.subheader("📋 Dữ liệu mẫu")
    st.dataframe(df.head(10), use_container_width=True)

else:
    st.subheader("📂 Chọn dữ liệu đầu vào")

    source = st.radio(
        "Nguồn dữ liệu",
        ["Dữ liệu có sẵn", "Tải file CSV"],
        horizontal=True,
    )

    if source == "Tải file CSV":
        uploaded = st.file_uploader(
            "Chọn file CSV",
            type=["csv"],
        )
        if uploaded is None:
            st.info("Hãy tải file CSV lên để tiếp tục.")
            st.stop()
        try:
            input_df = pd.read_csv(uploaded)
        except Exception as e:
            st.error(f"Không đọc được file CSV: {e}")
            st.stop()
    else:
        number = st.number_input(
            "Số sách muốn dự đoán",
            min_value=1,
            max_value=min(100, len(df)),
            value=min(5, len(df)),
        )
        input_df = df.head(int(number)).copy()

    st.write("**Dữ liệu đầu vào:**")
    st.dataframe(input_df.head(20), use_container_width=True)

    if page == "Dự đoán thể loại":
        st.subheader("🏷️ Dự đoán thể loại sách")

        if st.button("Dự đoán thể loại", type="primary"):
            try:
                labels = predict_classification(input_df)
                result = input_df.copy()
                result["Thể loại dự đoán"] = labels
                st.success("Dự đoán thành công!")
                st.dataframe(result, use_container_width=True)
            except Exception as e:
                st.error(f"Lỗi dự đoán: {e}")

    elif page == "Dự đoán giá sách":
        st.subheader("💷 Dự đoán giá sách")

        if st.button("Dự đoán giá", type="primary"):
            try:
                prices = predict_regression(input_df)
                result = input_df.copy()
                result["Giá dự đoán (GBP)"] = prices
                st.success("Dự đoán thành công!")
                st.dataframe(result, use_container_width=True)
            except Exception as e:
                st.error(f"Lỗi dự đoán: {e}")

    elif page == "Phân cụm K-Means":
        st.subheader("🔍 Phân cụm sách")

        use_pca = st.checkbox(
            "Sử dụng PCA (giảm chiều dữ liệu)",
            value=False,
        )

        if st.button("Phân cụm sách", type="primary"):
            try:
                labels = predict_clustering(
                    input_df,
                    use_pca=use_pca,
                )
                result = input_df.copy()
                result["Cụm dự đoán"] = labels
                st.success("Phân cụm thành công!")
                st.dataframe(result, use_container_width=True)

                st.subheader("Phân bố các cụm")
                counts = result["Cụm dự đoán"].value_counts()
                st.bar_chart(counts)

            except Exception as e:
                st.error(f"Lỗi phân cụm: {e}")

    elif page == "Dự đoán tổng hợp":
        st.subheader("🧠 Tích hợp 3 mô hình")

        if st.button("Chạy dự đoán tổng hợp", type="primary"):
            try:
                result = predict_all(
                    input_df,
                    include_clustering=True,
                    use_pca=False,
                )

                st.success("Tích hợp 3 mô hình thành công!")
                st.dataframe(result, use_container_width=True)

                csv = result.to_csv(index=False).encode("utf-8-sig")
                st.download_button(
                    "📥 Tải kết quả CSV",
                    data=csv,
                    file_name="ket_qua_du_doan.csv",
                    mime="text/csv",
                )

            except Exception as e:
                st.error(f"Lỗi tích hợp: {e}")
