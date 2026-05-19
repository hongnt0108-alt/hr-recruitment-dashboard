import pandas as pd
import streamlit as st
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from db import get_engine
from page1 import apply_overview_filters, show_overview
from page2 import show_prediction
from page3 import show_key_insights


TABLE_NAME = "hr_attrition"


st.set_page_config(
    page_title="HR Attrition Dashboard",
    page_icon="📊",
    layout="wide",
)


@st.cache_data
def load_data() -> pd.DataFrame:
    engine = get_engine()
    query = text(f"SELECT * FROM {TABLE_NAME}")

    with engine.connect() as conn:
        df = pd.read_sql_query(query, conn)

    return df


def render_header() -> None:
    st.title("📊 HR Attrition Analytics Dashboard")
    st.markdown(
        """
        Dashboard này giúp theo dõi tổng quan tình hình nhân sự tại công ty.
        """
    )


def render_sidebar() -> str:
    return st.sidebar.radio(
        "Navigation",
        [
            "Overview",
            "Attrition Insights",
            "Prediction",
        ],
    )


def render_page(page: str, df: pd.DataFrame) -> None:
    if page == "Overview":
        filtered_df = apply_overview_filters(df)
        show_overview(filtered_df)

    elif page == "Attrition Insights":
        show_key_insights(df)

    elif page == "Prediction":
        show_prediction(df)


def main() -> None:
    render_header()

    try:
        df = load_data()
    except SQLAlchemyError as error:
        st.error(
            "Không thể tải dữ liệu từ database. "
            "Hãy kiểm tra DATABASE_URL trong file .env và đảm bảo đã chạy `python src/upload_data.py`."
        )
        st.exception(error)
        return

    if df.empty:
        st.warning(
            "Database hiện chưa có dữ liệu. "
            "Hãy chạy lần lượt: `download_data.py`, `clean_data.py`, `upload_data.py`."
        )
        return

    page = render_sidebar()
    render_page(page, df)


if __name__ == "__main__":
    main()