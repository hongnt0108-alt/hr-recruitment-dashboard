import pandas as pd
import plotly.express as px
import streamlit as st


# =========================
# STYLE
# =========================

def inject_css() -> None:
    st.markdown(
        """
        <style>
        .kpi-card {
            background: linear-gradient(135deg, #ffffff 0%, #f7f9fc 100%);
            padding: 20px;
            border-radius: 18px;
            border: 1px solid #e6eaf0;
            box-shadow: 0 6px 18px rgba(0, 0, 0, 0.06);
            height: 125px;
        }

        .kpi-title {
            font-size: 14px;
            color: #6b7280;
            margin-bottom: 8px;
        }

        .kpi-value {
            font-size: 30px;
            font-weight: 700;
            color: #111827;
        }

        .section-card {
            background: #ffffff;
            padding: 18px;
            border-radius: 18px;
            border: 1px solid #e6eaf0;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.04);
            margin-bottom: 18px;
        }

        .insight-box {
            background: #f8fafc;
            border-left: 5px solid #2563eb;
            padding: 16px;
            border-radius: 12px;
            margin-bottom: 18px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# =========================
# HELPER FUNCTIONS
# =========================

def has_required_columns(df: pd.DataFrame, columns: list[str]) -> bool:
    missing_columns = [col for col in columns if col not in df.columns]

    if missing_columns:
        st.warning(
            "Thiếu cột dữ liệu: "
            + ", ".join(f"`{col}`" for col in missing_columns)
        )
        return False

    return True


def prepare_attrition_flag(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    if "Attrition" not in df.columns:
        raise ValueError("Không tìm thấy cột 'Attrition' trong dữ liệu.")

    if df["Attrition"].dtype == "object":
        df["AttritionFlag"] = (
            df["Attrition"]
            .astype(str)
            .str.strip()
            .str.lower()
            .map(
                {
                    "yes": 1,
                    "no": 0,
                    "1": 1,
                    "0": 0,
                }
            )
        )
    else:
        df["AttritionFlag"] = df["Attrition"]

    df["AttritionFlag"] = df["AttritionFlag"].fillna(0).astype(int)

    return df


def calculate_attrition_rate(df: pd.DataFrame, group_col: str) -> pd.DataFrame:
    if group_col not in df.columns:
        return pd.DataFrame(
            columns=[
                group_col,
                "TotalEmployees",
                "AttritionEmployees",
                "AttritionRate",
            ]
        )

    df = prepare_attrition_flag(df)

    result = (
        df.groupby(group_col, as_index=False, observed=False)
        .agg(
            TotalEmployees=("AttritionFlag", "count"),
            AttritionEmployees=("AttritionFlag", "sum"),
        )
    )

    if result.empty:
        return result

    result["AttritionRate"] = (
        result["AttritionEmployees"]
        / result["TotalEmployees"]
        * 100
    )

    result = result.sort_values(
        by="AttritionRate",
        ascending=False,
    )

    return result


def get_attrition_group(rate: float) -> str:
    if rate < 10:
        return "Low"
    if rate < 20:
        return "Medium"
    return "High"


def get_bar_colors(chart_df: pd.DataFrame) -> pd.Series:
    color_map = {
        "Low": "#A8DADC",
        "Medium": "#F4A261",
        "High": "#E63946",
    }

    groups = chart_df["AttritionRate"].apply(get_attrition_group)

    return groups.map(color_map)


def create_age_group(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    if "Age" not in df.columns:
        return df

    df["AgeGroup"] = pd.cut(
        df["Age"],
        bins=[0, 25, 35, 45, 55, 100],
        labels=[
            "Under 25",
            "25-34",
            "35-44",
            "45-54",
            "55+",
        ],
    )

    return df


def create_income_group(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    if "MonthlyIncome" not in df.columns:
        return df

    try:
        df["IncomeGroup"] = pd.qcut(
            df["MonthlyIncome"],
            q=4,
            labels=[
                "Low Income",
                "Mid-Low Income",
                "Mid-High Income",
                "High Income",
            ],
            duplicates="drop",
        )
    except ValueError:
        df["IncomeGroup"] = "Unknown"

    return df


def create_years_company_group(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    if "YearsAtCompany" not in df.columns:
        return df

    df["YearsAtCompanyGroup"] = pd.cut(
        df["YearsAtCompany"],
        bins=[-1, 1, 5, 10, 100],
        labels=[
            "0-1 years",
            "2-5 years",
            "6-10 years",
            "10+ years",
        ],
    )

    return df


# =========================
# CHART FUNCTIONS
# =========================

def show_attrition_bar(
    df: pd.DataFrame,
    group_col: str,
    title: str,
    height: int = 420,
) -> pd.DataFrame:
    chart_df = calculate_attrition_rate(df, group_col)

    if chart_df.empty:
        st.warning(f"Không có dữ liệu phù hợp để hiển thị biểu đồ `{title}`.")
        return chart_df

    fig = px.bar(
        chart_df,
        x=group_col,
        y="AttritionRate",
        text=chart_df["AttritionRate"].round(2),
        hover_data=[
            "TotalEmployees",
            "AttritionEmployees",
        ],
        title=title,
        category_orders={
            group_col: chart_df[group_col].astype(str).tolist(),
        },
    )

    fig.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside",
        marker_color=get_bar_colors(chart_df),
        width=0.55,
    )

    y_max = chart_df["AttritionRate"].max()

    fig.update_layout(
        height=height,
        yaxis_title="Attrition Rate (%)",
        xaxis_title="",
        yaxis=dict(range=[0, y_max * 1.25 if y_max > 0 else 1]),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        uniformtext_minsize=8,
        uniformtext_mode="hide",
        showlegend=False,
        margin=dict(l=30, r=30, t=70, b=80),
    )

    st.plotly_chart(fig, width="stretch")

    return chart_df


def show_count_bar(
    df: pd.DataFrame,
    group_col: str,
    title: str,
    height: int = 420,
) -> pd.DataFrame:
    if group_col not in df.columns:
        st.warning(f"Không tìm thấy cột `{group_col}` để hiển thị biểu đồ.")
        return pd.DataFrame()

    chart_df = (
        df[group_col]
        .value_counts()
        .reset_index()
    )

    chart_df.columns = [group_col, "Count"]

    if chart_df.empty:
        st.warning(f"Không có dữ liệu phù hợp để hiển thị biểu đồ `{title}`.")
        return chart_df

    fig = px.bar(
        chart_df,
        x=group_col,
        y="Count",
        text="Count",
        title=title,
    )

    fig.update_traces(
        textposition="outside",
        marker_color="#457B9D",
        width=0.55,
    )

    fig.update_layout(
        height=height,
        yaxis_title="Employee Count",
        xaxis_title="",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        margin=dict(l=30, r=30, t=70, b=80),
    )

    st.plotly_chart(fig, width="stretch")

    return chart_df


def show_box_plot(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    yaxis_title: str,
) -> None:
    if x_col not in df.columns or y_col not in df.columns:
        st.warning(f"Không đủ dữ liệu để hiển thị biểu đồ `{title}`.")
        return

    fig = px.box(
        df,
        x=x_col,
        y=y_col,
        title=title,
    )

    fig.update_layout(
        height=430,
        xaxis_title=x_col,
        yaxis_title=yaxis_title,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )

    st.plotly_chart(fig, width="stretch")


# =========================
# SIDEBAR FILTERS
# =========================

def apply_overview_filters(df: pd.DataFrame) -> pd.DataFrame:
    required_columns = [
        "Department",
        "JobRole",
        "Gender",
        "OverTime",
        "Age",
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        st.sidebar.warning(
            "Thiếu cột filter: "
            + ", ".join(missing_columns)
        )
        return df

    st.sidebar.title("🔎 Filters")

    department_options = sorted(df["Department"].dropna().unique())
    jobrole_options = sorted(df["JobRole"].dropna().unique())
    gender_options = sorted(df["Gender"].dropna().unique())
    overtime_options = sorted(df["OverTime"].dropna().unique())

    department_filter = st.sidebar.multiselect(
        "Department",
        options=department_options,
        default=department_options,
    )

    jobrole_filter = st.sidebar.multiselect(
        "Job Role",
        options=jobrole_options,
        default=jobrole_options,
    )

    gender_filter = st.sidebar.multiselect(
        "Gender",
        options=gender_options,
        default=gender_options,
    )

    overtime_filter = st.sidebar.multiselect(
        "OverTime",
        options=overtime_options,
        default=overtime_options,
    )

    age_min = int(df["Age"].min())
    age_max = int(df["Age"].max())

    age_range = st.sidebar.slider(
        "Age Range",
        min_value=age_min,
        max_value=age_max,
        value=(age_min, age_max),
    )

    filtered_df = df[
        (df["Department"].isin(department_filter))
        & (df["JobRole"].isin(jobrole_filter))
        & (df["Gender"].isin(gender_filter))
        & (df["OverTime"].isin(overtime_filter))
        & (df["Age"].between(age_range[0], age_range[1]))
    ]

    return filtered_df


# =========================
# KPI CARD
# =========================

def show_kpi_card(title: str, value: str) -> None:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def get_average_value(df: pd.DataFrame, column: str) -> float:
    if column not in df.columns:
        return 0.0

    return float(df[column].mean())


# =========================
# PAGE SECTIONS
# =========================

def show_kpi_section(df: pd.DataFrame) -> None:
    total_employees = len(df)
    attrition_employees = int(df["AttritionFlag"].sum())
    active_employees = total_employees - attrition_employees
    attrition_rate = attrition_employees / total_employees * 100

    average_age = get_average_value(df, "Age")
    average_income = get_average_value(df, "MonthlyIncome")
    average_years_company = get_average_value(df, "YearsAtCompany")
    performance_rating = get_average_value(df, "PerformanceRating")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        show_kpi_card("Total Employees", f"{total_employees:,}")

    with col2:
        show_kpi_card("Attrition Employees", f"{attrition_employees:,}")

    with col3:
        show_kpi_card("Active Employees", f"{active_employees:,}")

    with col4:
        show_kpi_card("Attrition Rate", f"{attrition_rate:.2f}%")

    st.write("")

    col5, col6, col7, col8 = st.columns(4)

    with col5:
        show_kpi_card("Average Age", f"{average_age:.1f}")

    with col6:
        show_kpi_card("Avg Monthly Income", f"${average_income:,.0f}")

    with col7:
        show_kpi_card("Avg Years at Company", f"{average_years_company:.1f}")

    with col8:
        show_kpi_card("Performance Rating", f"{performance_rating:.1f}")


def show_job_department_tab(df: pd.DataFrame) -> None:
    st.markdown(
        """
        <div class="insight-box">
        <b>Focus:</b> Phân tích Attrition theo phòng ban và vị trí công việc.
        Mục này giúp HR xác định nhóm công việc nào có tỷ lệ nghỉ việc cao nhất.
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        show_attrition_bar(
            df,
            "Department",
            "Attrition Rate by Department",
        )

    with col2:
        show_count_bar(
            df,
            "Department",
            "Employee Count by Department",
        )

    show_attrition_bar(
        df,
        "JobRole",
        "Attrition Rate by Job Role",
        height=500,
    )


def show_work_conditions_tab(df: pd.DataFrame) -> None:
    st.markdown(
        """
        <div class="insight-box">
        <b>Focus:</b> Phân tích điều kiện làm việc như overtime, business travel,
        work-life balance và job satisfaction.
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        show_attrition_bar(
            df,
            "OverTime",
            "Attrition Rate by OverTime",
        )

    with col2:
        show_attrition_bar(
            df,
            "BusinessTravel",
            "Attrition Rate by Business Travel",
        )

    col3, col4 = st.columns(2)

    with col3:
        show_attrition_bar(
            df,
            "WorkLifeBalance",
            "Attrition Rate by Work Life Balance",
        )

    with col4:
        show_attrition_bar(
            df,
            "JobSatisfaction",
            "Attrition Rate by Job Satisfaction",
        )


def show_demographics_tab(df: pd.DataFrame) -> None:
    st.markdown(
        """
        <div class="insight-box">
        <b>Focus:</b> Phân tích Attrition theo nhóm tuổi, giới tính,
        tình trạng hôn nhân và lĩnh vực học vấn.
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        show_attrition_bar(
            df,
            "AgeGroup",
            "Attrition Rate by Age Group",
        )

    with col2:
        show_attrition_bar(
            df,
            "Gender",
            "Attrition Rate by Gender",
        )

    col3, col4 = st.columns(2)

    with col3:
        show_attrition_bar(
            df,
            "MaritalStatus",
            "Attrition Rate by Marital Status",
        )

    with col4:
        show_attrition_bar(
            df,
            "EducationField",
            "Attrition Rate by Education Field",
        )


def show_income_tenure_tab(df: pd.DataFrame) -> None:
    st.markdown(
        """
        <div class="insight-box">
        <b>Focus:</b> Phân tích mối liên hệ giữa thu nhập, thời gian làm việc
        và khả năng nghỉ việc.
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        show_attrition_bar(
            df,
            "IncomeGroup",
            "Attrition Rate by Income Group",
        )

    with col2:
        show_attrition_bar(
            df,
            "YearsAtCompanyGroup",
            "Attrition Rate by Years at Company",
        )

    col3, col4 = st.columns(2)

    with col3:
        show_box_plot(
            df,
            x_col="Attrition",
            y_col="MonthlyIncome",
            title="Monthly Income Distribution by Attrition",
            yaxis_title="Monthly Income",
        )

    with col4:
        show_box_plot(
            df,
            x_col="Attrition",
            y_col="YearsAtCompany",
            title="Years at Company Distribution by Attrition",
            yaxis_title="Years at Company",
        )


def show_filtered_data(df: pd.DataFrame) -> None:
    with st.expander("View Filtered Data"):
        preview_columns = [
            "Age",
            "Gender",
            "Department",
            "JobRole",
            "MonthlyIncome",
            "YearsAtCompany",
            "OverTime",
            "Attrition",
        ]

        available_preview_columns = [
            col for col in preview_columns
            if col in df.columns
        ]

        if not available_preview_columns:
            st.warning("Không có cột phù hợp để hiển thị dữ liệu.")
            return

        st.dataframe(
            df[available_preview_columns],
            width="stretch",
        )


# =========================
# PAGE 1 MAIN
# =========================

def show_overview(filtered_df: pd.DataFrame) -> None:
    inject_css()

    st.subheader("Overview")

    try:
        df = prepare_attrition_flag(filtered_df)
    except ValueError as error:
        st.error("Không thể xử lý dữ liệu Attrition.")
        st.exception(error)
        return

    total_employees = len(df)

    if total_employees == 0:
        st.warning("Không có dữ liệu phù hợp với filter hiện tại.")
        return

    df = create_age_group(df)
    df = create_income_group(df)
    df = create_years_company_group(df)

    show_kpi_section(df)

    st.divider()

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "Job & Department",
            "Work Conditions",
            "Demographics",
            "Income & Tenure",
        ]
    )

    with tab1:
        show_job_department_tab(df)

    with tab2:
        show_work_conditions_tab(df)

    with tab3:
        show_demographics_tab(df)

    with tab4:
        show_income_tenure_tab(df)

    st.divider()

    show_filtered_data(df)