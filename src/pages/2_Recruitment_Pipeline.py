import pandas as pd
import streamlit as st
import plotly.express as px
from sqlalchemy.exc import SQLAlchemyError

from dashboard_utils import (
    BLUE_COLORS,
    apply_custom_style,
    render_header,
    render_page_title,
    load_data,
    filter_by_sidebar,
    apply_chart_style,
    show_database_error,
    check_empty_data,
)


st.set_page_config(
    page_title="🌐 Recruitment Pipeline | Recruitment Dashboard",
    page_icon="",
    layout="wide",
)


def show_recruitment_pipeline() -> None:
    apply_custom_style()
    render_header()
    render_page_title(
        "2. Recruitment Pipeline",
        "Theo dõi funnel ứng viên từ CV nhận được đến phỏng vấn, offer, onboard và failed.",
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

    total_cvs = len(cvs_df)

    total_interviews = (
        cvs_df["Ngày phỏng vấn"].notna().sum()
        if "Ngày phỏng vấn" in cvs_df.columns 
        else 0
    )

    total_offers = (
        cvs_df["Ngày Onboard"].notna().sum()
        if "Ngày Onboard" in cvs_df.columns
        else 0
    )
    total_onboards = (
        cvs_df[
            cvs_df["Ngày Onboard"].replace("NULL", pd.NA).notna()
            & (
                cvs_df["Kết quả tuyển dụng"]
                .astype(str)
                .str.strip()
                .str.lower()
                != "failed"
            )
        ].shape[0]
        if "Ngày Onboard" in cvs_df.columns and "Kết quả tuyển dụng" in cvs_df.columns
        else 0
    )

    total_failed = (
        len(
            cvs_df[
                cvs_df["Kết quả tuyển dụng"]
                .astype(str)
                .str.lower()
                .eq("failed")
            ]
        )
        if "Kết quả tuyển dụng" in cvs_df.columns
        else 0
    )

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("CV nhận được", f"{total_cvs:,}")
    col2.metric("Có lịch phỏng vấn", f"{total_interviews:,}")
    col3.metric("Offer", f"{total_offers:,}")
    col4.metric("Onboard", f"{total_onboards:,}")
    col5.metric("Failed", f"{total_failed:,}")

    funnel_df = pd.DataFrame(
        {
            "stage": [
                "CV nhận được",
                "Có lịch phỏng vấn",
                "Offer",
                "Onboard",
                "Failed",
            ],
            "count": [
                total_cvs,
                total_interviews,
                total_offers,
                total_onboards,
                total_failed,
            ],
        }
    )

    fig = px.funnel(
        funnel_df,
        x="count",
        y="stage",
        title="Funnel tuyển dụng",
        color_discrete_sequence=BLUE_COLORS,
    )

    fig = apply_chart_style(fig)
    
    st.plotly_chart(fig, use_container_width=True)

    left, right = st.columns(2)

    with left:
        st.subheader("Ứng viên theo trạng thái hiện tại")

        if "Trạng thái hiện tại" in cvs_df.columns:
            chart_df = (
                cvs_df.groupby("Trạng thái hiện tại")
                .size()
                .reset_index(name="Số lượng")
                .sort_values("Số lượng", ascending=False)
            )

            fig = px.bar(
                chart_df,
                x="Trạng thái hiện tại",
                y="Số lượng",
                text="Số lượng",
                color_discrete_sequence=BLUE_COLORS,
            )

            fig = apply_chart_style(fig)
            fig.update_layout(title_text="")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Không có cột Trạng thái hiện tại.")

    with right:
        st.subheader("Failed State")

        if "Failed State" in cvs_df.columns:
            chart_df = (
                cvs_df.groupby("Failed State")
                .size()
                .reset_index(name="Số lượng")
                .sort_values("Số lượng", ascending=False)
                .head(10)
            )

            fig = px.bar(
                chart_df,
                x="Số lượng",
                y="Failed State",
                orientation="h",
                text="Số lượng",
                color_discrete_sequence=BLUE_COLORS,
            )

            fig = apply_chart_style(fig)
            fig.update_layout(title_text="")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Không có cột Failed State.")

    st.subheader("Danh sách ứng viên active")

    if "Kết quả tuyển dụng" in cvs_df.columns:
        active_df = cvs_df[
            ~cvs_df["Kết quả tuyển dụng"]
            .astype(str)
            .str.lower()
            .isin(["failed", "done"])
        ]
    else:
        active_df = cvs_df

    st.dataframe(active_df, use_container_width=True, hide_index=True)


show_recruitment_pipeline()