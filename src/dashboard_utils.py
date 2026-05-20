import pandas as pd
import streamlit as st
import plotly.express as px
from sqlalchemy import text

from db import get_engine


ORDER_TABLE = "orders"
CV_TABLE = "cvs"
COST_TABLE = "costs"

BLUE_COLORS = [
    "#38BDF8",  # Cyan blue
    "#2DD4BF",  # Teal
    "#818CF8",  # Soft indigo
    "#A78BFA",  # Violet
    "#F472B6",  # Pink
    "#FB923C",  # Orange
    "#A3E635",  # Lime
    "#E2E8F0",  # Slate white
]


def apply_custom_style() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(135deg, #020617 0%, #0f172a 45%, #082f49 100%);
            color: #e0f2fe;
        }

        h1, h2, h3 {
            color: #38bdf8 !important;
            font-weight: 700 !important;
        }

        h1 {
            text-shadow: 0 0 18px rgba(56, 189, 248, 0.45);
        }

        p, label, span, div {
            color: #e0f2fe;
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #020617 0%, #0f172a 100%);
            border-right: 1px solid rgba(56, 189, 248, 0.25);
        }

        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3,
        section[data-testid="stSidebar"] label {
            color: #7dd3fc !important;
        }

        div[role="radiogroup"] label {
            background: rgba(15, 23, 42, 0.85);
            border: 1px solid rgba(56, 189, 248, 0.2);
            border-radius: 12px;
            padding: 8px 12px;
            margin-bottom: 6px;
        }

        div[role="radiogroup"] label:hover {
            border-color: #38bdf8;
            background: rgba(14, 165, 233, 0.16);
        }

        div[data-testid="stMetric"] {
            background: linear-gradient(145deg, rgba(15, 23, 42, 0.95), rgba(12, 74, 110, 0.72));
            border: 1px solid rgba(56, 189, 248, 0.35);
            border-radius: 18px;
            padding: 18px 20px;
            box-shadow: 0 0 24px rgba(14, 165, 233, 0.18);
        }

        div[data-testid="stMetric"] label {
            color: #bae6fd !important;
            font-size: 0.9rem !important;
        }

        div[data-testid="stMetricValue"] {
            color: #67e8f9 !important;
            font-size: 1.85rem !important;
            font-weight: 800 !important;
        }

        div[data-testid="stDataFrame"] {
            border: 1px solid rgba(56, 189, 248, 0.25);
            border-radius: 16px;
            overflow: hidden;
            box-shadow: 0 0 20px rgba(14, 165, 233, 0.12);
        }

        div[data-testid="stPlotlyChart"] {
            background: rgba(15, 23, 42, 0.72);
            border: 1px solid rgba(56, 189, 248, 0.2);
            border-radius: 18px;
            padding: 12px;
            box-shadow: 0 0 22px rgba(14, 165, 233, 0.14);
        }

        button[data-baseweb="tab"] {
            color: #bae6fd;
            background: rgba(15, 23, 42, 0.7);
            border-radius: 12px 12px 0 0;
        }

        button[data-baseweb="tab"][aria-selected="true"] {
            color: #67e8f9;
            border-bottom: 2px solid #38bdf8;
        }

        div[data-baseweb="select"] > div {
            background: #ffffff !important;
            border: 1px solid #38bdf8 !important;
            border-radius: 10px !important;
        }
        /* Tag đã chọn trong multiselect */
        div[data-baseweb="tag"] {
            background-color: #38bdf8 !important;
            color: #0f172a !important;
        }

        /* Chữ trong tag */
        div[data-baseweb="tag"] span {
            color: #0f172a !important;
        }

        /* Nút x */
        div[data-baseweb="tag"] svg {
            fill: #0f172a !important;
        }
        /* Chữ trong ô select */
        div[data-baseweb="select"] span,
        div[data-baseweb="select"] div {
            color: #0f172a !important;
        }

        /* Dropdown list */
        div[data-baseweb="popover"] ul,
        div[data-baseweb="menu"] {
            background: #ffffff !important;
        }

        /* Chữ trong dropdown */
        div[data-baseweb="popover"] li,
        div[data-baseweb="popover"] div,
        div[data-baseweb="popover"] span,
        [data-baseweb="menu"] li,
        [data-baseweb="menu"] div,
        [data-baseweb="menu"] span {
            color: #0f172a !important;
            background: #ffffff !important;
        }

        /* Hover item */
        div[data-baseweb="popover"] li:hover,
        [data-baseweb="menu"] li:hover {
            background: #e0f2fe !important;
        }

        [data-baseweb="menu"] li:hover {
            background: rgba(30, 41, 59, 0.25) !important;
        }

        input {
            color: #1e293b !important;
        }

        .stButton button {
            background: linear-gradient(90deg, #0284c7, #06b6d4);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 0.55rem 1rem;
            font-weight: 700;
            box-shadow: 0 0 18px rgba(6, 182, 212, 0.35);
        }

        .stButton button:hover {
            background: linear-gradient(90deg, #0369a1, #0891b2);
            box-shadow: 0 0 26px rgba(6, 182, 212, 0.55);
        }

        hr {
            border-color: rgba(56, 189, 248, 0.25);
        }

        div[data-testid="stAlert"] {
            border-radius: 14px;
            border: 1px solid rgba(56, 189, 248, 0.25);
        }

        #MainMenu {
            visibility: hidden;
        }

        footer {
            visibility: hidden;
        }

        header {
            background: transparent;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    st.markdown(
        """
        <div style="
            padding: 26px 30px;
            border-radius: 24px;
            background: linear-gradient(135deg, rgba(14,165,233,0.22), rgba(6,182,212,0.08));
            border: 1px solid rgba(56,189,248,0.35);
            box-shadow: 0 0 32px rgba(14,165,233,0.20);
            margin-bottom: 24px;
        ">
            <h1 style="margin-bottom: 8px;"> Recruitment Intelligence Dashboard</h1>
            <p style="font-size: 1.05rem; color: #bae6fd;">
                Theo dõi nhu cầu tuyển dụng, pipeline ứng viên, hiệu quả nguồn tuyển và chi phí tuyển dụng.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_page_title(title: str, description: str) -> None:
    st.markdown(
        f"""
        <div style="
            padding: 18px 22px;
            border-radius: 18px;
            background: rgba(14, 165, 233, 0.12);
            border: 1px solid rgba(56, 189, 248, 0.25);
            margin-bottom: 20px;
        ">
            <h2 style="margin-bottom: 6px;">{title}</h2>
            <p style="color: #bae6fd; margin-bottom: 0;">{description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def apply_chart_style(fig):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15,23,42,0.65)",
        font=dict(
            color="#e0f2fe",
            family="Arial",
        ),
        title=dict(
            font=dict(
                color="#67e8f9",
                size=18,
            )
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e0f2fe"),
        ),
        margin=dict(l=20, r=20, t=55, b=30),
    )

    fig.update_xaxes(
        gridcolor="rgba(148, 163, 184, 0.18)",
        linecolor="rgba(56, 189, 248, 0.25)",
        tickfont=dict(color="#bae6fd"),
        title_font=dict(color="#bae6fd"),
    )

    fig.update_yaxes(
        gridcolor="rgba(148, 163, 184, 0.18)",
        linecolor="rgba(56, 189, 248, 0.25)",
        tickfont=dict(color="#bae6fd"),
        title_font=dict(color="#bae6fd"),
    )

    return fig


@st.cache_data(ttl=300)
def load_table(table_name: str) -> pd.DataFrame:
    engine = get_engine()
    query = text(f"SELECT * FROM {table_name}")

    with engine.connect() as conn:
        df = pd.read_sql_query(query, conn)

    return df


@st.cache_data(ttl=300)
def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    orders_df = load_table(ORDER_TABLE)
    cvs_df = load_table(CV_TABLE)
    costs_df = load_table(COST_TABLE)

    orders_df = prepare_dates(
        orders_df,
        [
            "request_date",
            "expected_onboard_date",
            "approval_date",
            "expected_interview_start_date",
            "expected_offer_date",
            "latest_onboard_date",
            "recruitment_start_date",
            "recruitment_end_date",
        ],
    )

    cvs_df = prepare_dates(
        cvs_df,
        [
            "applied_date",
            "interview_date",
            "onboard_date",
        ],
    )

    return orders_df, cvs_df, costs_df


def prepare_dates(df: pd.DataFrame, date_columns: list[str]) -> pd.DataFrame:
    df = df.copy()

    for col in date_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    return df


def safe_divide(numerator, denominator):
    if denominator in [0, None] or pd.isna(denominator):
        return 0

    return numerator / denominator


def format_money(value):
    if pd.isna(value):
        return "0 VND"

    return f"{value:,.0f} VND"


def filter_by_sidebar(
    orders_df: pd.DataFrame,
    cvs_df: pd.DataFrame,
    costs_df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:

    st.sidebar.markdown("## ⚙️ Bộ lọc")

    orders_df = orders_df.copy()
    cvs_df = cvs_df.copy()
    costs_df = costs_df.copy()

    department_options = []

    if "Phòng ban" in orders_df.columns:
        department_options.extend(orders_df["Phòng ban"].dropna().unique())

    if "Phòng ban" in cvs_df.columns:
        department_options.extend(cvs_df["Phòng ban"].dropna().unique())

    if "Phòng ban" in costs_df.columns:
        department_options.extend(costs_df["Phòng ban"].dropna().unique())

    department_options = sorted(set(department_options))

    selected_departments = st.sidebar.multiselect(
        "Phòng ban",
        department_options,
    )

    if selected_departments:
        if "Phòng ban" in orders_df.columns:
            orders_df = orders_df[orders_df["Phòng ban"].isin(selected_departments)]

        if "Phòng ban" in cvs_df.columns:
            cvs_df = cvs_df[cvs_df["Phòng ban"].isin(selected_departments)]

        if "Phòng ban" in costs_df.columns:
            costs_df = costs_df[costs_df["Phòng ban"].isin(selected_departments)]

    job_options = []

    if "Vị trí cần tuyển" in orders_df.columns:
        job_options.extend(orders_df["Vị trí cần tuyển"].dropna().unique())

    if "Vị trí ứng tuyển" in cvs_df.columns:
        job_options.extend(cvs_df["Vị trí ứng tuyển"].dropna().unique())

    if "Vị trí tuyển dụng" in costs_df.columns:
        job_options.extend(costs_df["Vị trí tuyển dụng"].dropna().unique())

    job_options = sorted(set(job_options))

    selected_jobs = st.sidebar.multiselect(
        "Vị trí tuyển dụng",
        job_options,
    )

    if selected_jobs:
        if "Vị trí cần tuyển" in orders_df.columns:
            orders_df = orders_df[orders_df["Vị trí cần tuyển"].isin(selected_jobs)]

        if "Vị trí ứng tuyển" in cvs_df.columns:
            cvs_df = cvs_df[cvs_df["Vị trí ứng tuyển"].isin(selected_jobs)]

        if "Vị trí tuyển dụng" in costs_df.columns:
            costs_df = costs_df[costs_df["Vị trí tuyển dụng"].isin(selected_jobs)]

    # if "Nguồn tuyển dụng" in cvs_df.columns:
    #     source_options = sorted(cvs_df["Nguồn tuyển dụng"].dropna().unique())

    #     selected_sources = st.sidebar.multiselect(
    #         "Nguồn tuyển dụng",
    #         source_options,
    #     )

    #     if selected_sources:
    #         cvs_df = cvs_df[cvs_df["Nguồn tuyển dụng"].isin(selected_sources)]

    if "Nền tảng" in costs_df.columns:
        platform_options = sorted(costs_df["Nền tảng"].dropna().unique())

        selected_platforms = st.sidebar.multiselect(
            "Nền tảng",
            platform_options,
        )

        if selected_platforms:
            costs_df = costs_df[costs_df["Nền tảng"].isin(selected_platforms)]

    return orders_df, cvs_df, costs_df


def show_database_error(error) -> None:
    st.error(
        "Không thể tải dữ liệu từ Neon. "
        "Hãy kiểm tra DATABASE_URL và đảm bảo đã có 3 bảng: "
        "recruitment_orders, recruitment_cvs, recruitment_costs."
    )
    st.exception(error)


def check_empty_data(
    orders_df: pd.DataFrame,
    cvs_df: pd.DataFrame,
    costs_df: pd.DataFrame,
) -> bool:
    if orders_df.empty and cvs_df.empty and costs_df.empty:
        st.warning(
            "Database hiện chưa có dữ liệu. "
            "Hãy upload dữ liệu từ Orders.xlsx, CVs.xlsx và Cost.xlsx vào Neon trước."
        )
        return True

    return False