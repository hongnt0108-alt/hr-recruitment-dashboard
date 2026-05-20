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
    page_title="Job Orders | Recruitment Dashboard",
    page_icon="🌐",
    layout="wide",
)


def show_job_orders() -> None:
    apply_custom_style()
    render_header()
    render_page_title(
        "3. Job Order Dashboard",
        "Theo dõi nhu cầu tuyển dụng theo phòng ban, vị trí, headcount và trạng thái.",
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

    total_required = (
        orders_df["Số lượng cần tuyển"].sum()
        if "Số lượng cần tuyển" in orders_df.columns
        else 0
    )

    total_onboard = (
        orders_df["Số OB"].sum()
        if "Số OB" in orders_df.columns
        else 0
    )

    total_remaining = (
        orders_df["Còn cần tuyển"].sum()
        if "Còn cần tuyển" in orders_df.columns
        else 0
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Tổng order", f"{total_orders:,}")
    col2.metric("Tổng cần tuyển", f"{total_required:,.0f}")
    col3.metric("Tổng đã OB", f"{total_onboard:,.0f}")
    col4.metric("Còn cần tuyển", f"{total_remaining:,.0f}")

    left, right = st.columns(2)

    with left:
        st.subheader("Order theo tình trạng")

        if "State hiện tại" in orders_df.columns:
            chart_df = (
                orders_df.groupby("State hiện tại")
                .size()
                .reset_index(name="count")
                .sort_values("count", ascending=False)
            )

            fig = px.pie(
                chart_df,
                names="State hiện tại",
                values="count",
                color_discrete_sequence=BLUE_COLORS,
            )

            fig = apply_chart_style(fig)
            fig.update_layout(title_text="")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Không có cột State hiện tại.")

    with right:
        st.subheader("Headcount cần tuyển theo phòng ban")

        if "Phòng ban" in orders_df.columns and "Số lượng cần tuyển" in orders_df.columns:
            chart_df = (
                orders_df.groupby("Phòng ban")["Số lượng cần tuyển"]
                .sum()
                .reset_index()
                .sort_values("Số lượng cần tuyển", ascending=False)
            )

            fig = px.bar(
                chart_df,
                x="Phòng ban",
                y="Số lượng cần tuyển",
                text="Số lượng cần tuyển",
                color_discrete_sequence=BLUE_COLORS,
            )

            fig = apply_chart_style(fig)
            fig.update_layout(title_text="")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Không có cột Phòng ban hoặc Số lượng cần tuyển.")

    st.subheader("Hiệu quả theo vị trí")

    needed_cols = [
        "Vị trí cần tuyển",
        "Phòng ban",
        "Số lượng cần tuyển",
        "Số lượng CV đã nhận được",
        "Số phỏng vấn đã set",
        "Số OB",
        "Còn cần tuyển",
        "Trạng thái tuyển dụng",
    ]

    available_cols = [col for col in needed_cols if col in orders_df.columns]

    if available_cols:
        st.dataframe(
            orders_df[available_cols],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.dataframe(orders_df, use_container_width=True, hide_index=True)


show_job_orders()