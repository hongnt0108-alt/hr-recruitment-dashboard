import streamlit as st

from dashboard_utils import apply_custom_style, render_header


st.set_page_config(
    page_title="Recruitment Intelligence Dashboard",
    page_icon="🌐",
    layout="wide",
)


def main() -> None:
    apply_custom_style()
    render_header()

    st.markdown(
        """
        ### Chào mừng đến với Recruitment Intelligence Dashboard

        Sử dụng menu bên trái để chuyển giữa các màn hình:

        - **Overview**: Tổng quan tuyển dụng
        - **Recruitment Pipeline**: Funnel ứng viên
        - **Job Orders**: Theo dõi nhu cầu tuyển
        - **Source & Cost**: Hiệu quả nguồn tuyển và chi phí
        - **Detail Table**: Bảng dữ liệu chi tiết
        """
    )


if __name__ == "__main__":
    main()