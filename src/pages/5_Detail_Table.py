import streamlit as st
from sqlalchemy.exc import SQLAlchemyError

from dashboard_utils import (
    apply_custom_style,
    render_header,
    render_page_title,
    load_data,
    filter_by_sidebar,
    show_database_error,
    check_empty_data,
)


st.set_page_config(
    page_title="Detail Table | Recruitment Dashboard",
    page_icon="🚀",
    layout="wide",
)


def show_detail_table() -> None:
    apply_custom_style()
    render_header()
    render_page_title(
        "5. Detail Table",
        "Tra cứu dữ liệu chi tiết theo Job Orders, Candidate Pipeline và Cost Performance.",
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

    tab1, tab2, tab3 = st.tabs(
        [
            "Job Orders",
            "Candidate Pipeline",
            "Cost Performance",
        ]
    )

    with tab1:
        st.subheader("Job Orders")
        st.dataframe(orders_df, use_container_width=True, hide_index=True)

    with tab2:
        st.subheader("Candidate Pipeline")
        st.dataframe(cvs_df, use_container_width=True, hide_index=True)

    with tab3:
        st.subheader("Cost Performance")
        st.dataframe(costs_df, use_container_width=True, hide_index=True)


show_detail_table()