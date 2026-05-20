import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy.exc import SQLAlchemyError

from dashboard_utils import (
    BLUE_COLORS,
    apply_custom_style,
    render_header,
    render_page_title,
    load_data,
    filter_by_sidebar,
    safe_divide,
    format_money,
    apply_chart_style,
    show_database_error,
    check_empty_data,
)


st.set_page_config(
    page_title="Source & Cost | Recruitment Dashboard",
    page_icon="🚀",
    layout="wide",
)


def show_source_cost() -> None:
    apply_custom_style()
    render_header()
    render_page_title(
        "4. Source & Cost Dashboard",
        "Phân tích chi phí tuyển dụng, hiệu quả nền tảng và chi phí trên mỗi CV, interview, offer.",
    )

    try:
        orders_df, cvs_df, costs_df = load_data()
    except SQLAlchemyError as error:
        show_database_error(error)
        return

    if check_empty_data(orders_df, cvs_df, costs_df):
        return

    orders_df, cvs_df, costs_df = filter_by_sidebar(
        orders_df,
        cvs_df,
        costs_df,
    )

    total_cost = costs_df["Chi phí"].sum() if "Chi phí" in costs_df.columns else 0
    total_cv = costs_df["CV thu được"].sum() if "CV thu được" in costs_df.columns else 0

    total_interview = (
    cvs_df["Ngày phỏng vấn"].notna().sum()
    if "Ngày phỏng vấn" in cvs_df.columns 
    else 0
    )

    total_offer = (
        cvs_df["Ngày Onboard"].notna().sum()
        if "Ngày Onboard" in cvs_df.columns
        else 0
    )
    cost_per_cv = safe_divide(total_cost, total_cv)
    cost_per_interview = safe_divide(total_cost, total_interview)
    cost_per_offer = safe_divide(total_cost, total_offer)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Tổng chi phí", format_money(total_cost))
    col2.metric("Cost / CV", format_money(cost_per_cv))
    col3.metric("Cost / Interview", format_money(cost_per_interview))
    col4.metric("Cost / Offer", format_money(cost_per_offer))

    if costs_df.empty:
        st.warning("Không có dữ liệu chi phí.")
        return

    costs_df = costs_df.copy()

    if "Chi phí" in costs_df.columns and "CV thu được" in costs_df.columns:
        costs_df["cost_per_cv"] = costs_df.apply(
            lambda row: safe_divide(row["Chi phí"], row["CV thu được"]),
            axis=1,
        )

    if "Chi phí" in costs_df.columns and "Số phỏng vấn" in costs_df.columns:
        costs_df["cost_per_interview"] = costs_df.apply(
            lambda row: safe_divide(row["Chi phí"], row["Số phỏng vấn"]),
            axis=1,
        )

    if "Chi phí" in costs_df.columns and "Số offer chốt được" in costs_df.columns:
        costs_df["cost_per_offer"] = costs_df.apply(
            lambda row: safe_divide(row["Chi phí"], row["Số offer chốt được"]),
            axis=1,
        )

    left, right = st.columns(2)

    with left:
        st.subheader("Chi phí theo nền tảng")

        if "Nền tảng" in costs_df.columns and "Chi phí" in costs_df.columns:
            chart_df = (
                costs_df.groupby("Nền tảng")["Chi phí"]
                .sum()
                .reset_index()
                .sort_values("Chi phí", ascending=False)
            )

            fig = px.bar(
                chart_df,
                x="Nền tảng",
                y="Chi phí",
                text="Chi phí",
                color_discrete_sequence=BLUE_COLORS,
            )

            fig = apply_chart_style(fig)
            fig.update_layout(title_text="")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Không có cột Nền tảng hoặc Chi phí.")

    with right:
        st.subheader("CV thu được theo nền tảng")

        if "Nền tảng" in costs_df.columns and "CV thu được" in costs_df.columns:
            chart_df = (
                costs_df.groupby("Nền tảng")["CV thu được"]
                .sum()
                .reset_index()
                .sort_values("CV thu được", ascending=False)
            )

            fig = px.bar(
                chart_df,
                x="Nền tảng",
                y="CV thu được",
                text="CV thu được",
                color_discrete_sequence=BLUE_COLORS,
            )

            fig = apply_chart_style(fig)
            fig.update_layout(title_text="")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Không có cột Nền tảng hoặc CV thu được.")

    st.subheader("Chi phí vs CV thu được")

    if all(col in costs_df.columns for col in ["Chi phí", "CV thu được", "Nền tảng", "Vị trí tuyển dụng","Loại tin đăng"]):
        size_col = "Số offer chốt được" if "Số offer chốt được" in costs_df.columns else None

        fig = px.scatter(
            costs_df,
            x="Chi phí",
            y="CV thu được",
            size=size_col,
            color="Nền tảng",
            color_discrete_sequence=BLUE_COLORS,
            hover_data=[
                col
                for col in ["Chi phí", "CV thu được", "Nền tảng", "Vị trí tuyển dụng","Loại tin đăng"]
                if col in costs_df.columns
            ],
            title="Hiệu quả chi phí theo tin đăng",
        )

        fig = apply_chart_style(fig)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Cần có các cột Chi phí, CV thu được, Nền tảng để vẽ scatter chart.")

    st.subheader("Bảng hiệu quả chi phí")
    st.dataframe(costs_df, use_container_width=True, hide_index=True)


show_source_cost()