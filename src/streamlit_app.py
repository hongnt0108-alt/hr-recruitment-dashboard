import pandas as pd
import streamlit as st
from sqlalchemy import text

from db import get_engine
from page1 import apply_overview_filters, show_overview
from page2 import show_prediction
from page3 import show_key_insights

st.set_page_config(
    page_title="HR Attrition Dashboard",
    page_icon="📊",
    layout="wide"
)


@st.cache_data
def load_data():
    engine = get_engine()

    query = text("SELECT * FROM hr_attrition")

    with engine.connect() as conn:
        df = pd.read_sql_query(query, conn)

    return df


df = load_data()


st.title("📊 HR Attrition Analytics Dashboard")

st.markdown(
    """
    Dashboard này giúp theo dõi tổng quan tình hình nhân sự tại công ty.
    """
)


page = st.sidebar.radio(
    "Navigation",
    [
        "Overview",
        "Attrition Insights",
        "Prediction"
    ]
)



if page == "Overview":
    filtered_df = apply_overview_filters(df)
    show_overview(filtered_df)


elif page == "Attrition Insights":
    show_key_insights(df)


elif page == "Prediction":
    show_prediction(df)