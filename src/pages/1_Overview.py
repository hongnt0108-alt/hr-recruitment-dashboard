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
    page_title="Overview | Recruitment Dashboard",
    page_icon="🌐",
    layout="wide",
)


def show_overview() -> None:
    apply_custom_style()
    render_header()
    render_page_title(
        "1. Overview Dashboard",
        "Tổng quan nhu cầu tuyển dụng, CV, phỏng vấn, onboard và chi phí.",
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

    total_orders = len(orders_df)

    total_required_headcount = (
        orders_df["Số lượng cần tuyển"].sum()
        if "Số lượng cần tuyển" in orders_df.columns
        else 0
    )

    active_orders = (
        len(
            orders_df[
                orders_df["Tình trạng"]
                .astype(str)
                .str.lower()
                .str.contains("Đang tuyển", na=False)
            ]
        )
        if "Tình trạng" in orders_df.columns
        else 0
    )

    total_cvs = len(cvs_df)

    total_interviews = (
        cvs_df["Ngày phỏng vấn"].notna().sum()
        if "Ngày phỏng vấn" in cvs_df.columns
        else 0
    )

    total_onboards = (
        cvs_df["Ngày Onboard"].notna().sum()
        if "Ngày Onboard" in cvs_df.columns
        else 0
    )

    total_cost = costs_df["Chi phí"].sum() if "Chi phí" in costs_df.columns else 0
    cost_per_cv = safe_divide(total_cost, total_cvs)
    cost_per_onboard = safe_divide(total_cost, total_onboards)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Tổng request tuyển dụng", f"{total_orders:,}")
    col2.metric("Tổng headcount cần tuyển", f"{total_required_headcount:,.0f}")
    col3.metric("Order đang tuyển", f"{active_orders:,}")
    col4.metric("Tổng CV", f"{total_cvs:,}")

    col5, col6, col7, col8 = st.columns(4)
    col5.metric("Tổng phỏng vấn", f"{total_interviews:,}")
    col6.metric("Tổng Onboard", f"{total_onboards:,}")
    col7.metric("Cost / CV", format_money(cost_per_cv))
    col8.metric("Cost / Onboard", format_money(cost_per_onboard))

    st.divider()

    left, right = st.columns(2)

    with left:
        st.subheader("CV theo tháng")

        if "Ngày ứng tuyển" in cvs_df.columns:
            temp_df = cvs_df.dropna(subset=["Ngày ứng tuyển"]).copy()
            temp_df["Ngày ứng tuyển"] = pd.to_datetime(
                temp_df["Ngày ứng tuyển"],
                errors="coerce",
                dayfirst=True
                )
            temp_df["month"] = temp_df["Ngày ứng tuyển"].dt.to_period("M").astype(str)

            chart_df = (
                temp_df.groupby("month")
                .size()
                .reset_index(name="CVs count")
            )

            fig = px.bar(
                chart_df,
                x="month",
                y="CVs count",
                text="CVs count",
                title="CV nhận được theo tháng",
                color_discrete_sequence=BLUE_COLORS,
            )

            fig = apply_chart_style(fig)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Không có cột applied_date.")

    with right:
        st.subheader("Onboard theo tháng")

        if "Ngày Onboard" in cvs_df.columns:
            temp_df = cvs_df.dropna(subset=["Ngày Onboard"]).copy()
            temp_df["Ngày Onboard"] = pd.to_datetime(
                temp_df["Ngày Onboard"],
                errors="coerce",
                dayfirst=True
            )
            temp_df["month"] = temp_df["Ngày Onboard"].dt.to_period("M").astype(str)

            chart_df = (
                temp_df.groupby("month")
                .size()
                .reset_index(name="Ngày Onboard")
            )

            fig = px.bar(
                chart_df,
                x="month",
                y="Ngày Onboard",
                text="Ngày Onboard",
                title="Onboard theo tháng",
                color_discrete_sequence=BLUE_COLORS,
            )

            fig = apply_chart_style(fig)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Không có cột onboard_date.")

    left, right = st.columns(2)

    with left:
        st.subheader("CV theo nguồn tuyển dụng")

        if "Nguồn tuyển dụng" in cvs_df.columns:
            chart_df = (
                cvs_df.groupby("Nguồn tuyển dụng")
                .size()
                .reset_index(name="CVs count")
                .sort_values("CVs count", ascending=False)
            )

            fig = px.bar(
                chart_df,
                x="Nguồn tuyển dụng",
                y="CVs count",
                text="CVs count",
                title="CV theo nguồn",
                color_discrete_sequence=BLUE_COLORS,
            )

            fig = apply_chart_style(fig)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Không có cột source.")

    with right:
        st.subheader("Chi phí theo nền tảng")

        if "Nền tảng" in costs_df.columns and "Chi phí" in costs_df.columns:
            chart_df = (
                costs_df.groupby("Nền tảng")["Chi phí"]
                .sum()
                .reset_index()
                .sort_values("Chi phí", ascending=False)
            )

            fig = px.pie(
                chart_df,
                names="Nền tảng",
                values="Chi phí",
                title="Tỷ trọng chi phí theo nền tảng",
                color_discrete_sequence=BLUE_COLORS,
            )

            fig = apply_chart_style(fig)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Không có cột platform hoặc cost.")


show_overview()