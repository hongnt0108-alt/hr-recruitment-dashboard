import pandas as pd
import plotly.express as px
import streamlit as st


# =========================
# STYLE
# =========================

def inject_css():
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
        unsafe_allow_html=True
    )


# =========================
# HELPER FUNCTIONS
# =========================

def prepare_attrition_flag(df):
    df = df.copy()

    if df["Attrition"].dtype == "object":
        df["AttritionFlag"] = (
            df["Attrition"]
            .astype(str)
            .str.strip()
            .str.lower()
            .map({
                "yes": 1,
                "no": 0,
                "1": 1,
                "0": 0
            })
        )
    else:
        df["AttritionFlag"] = df["Attrition"]

    return df


def calculate_attrition_rate(df, group_col):
    df = prepare_attrition_flag(df)

    result = (
        df
        .groupby(group_col, as_index=False, observed=False)
        .agg(
            TotalEmployees=("AttritionFlag", "count"),
            AttritionEmployees=("AttritionFlag", "sum")
        )
    )

    result["AttritionRate"] = (
        result["AttritionEmployees"]
        / result["TotalEmployees"]
        * 100
    )

    result = result.sort_values(
        by="AttritionRate",
        ascending=False
    )

    return result


def get_attrition_group(rate):
    if rate < 10:
        return "Low"
    elif rate < 20:
        return "Medium"
    else:
        return "High"


def get_bar_colors(chart_df):
    color_map = {
        "Low": "#A8DADC",
        "Medium": "#F4A261",
        "High": "#E63946"
    }

    groups = chart_df["AttritionRate"].apply(get_attrition_group)
    return groups.map(color_map)


def show_attrition_bar(df, group_col, title, height=420):
    chart_df = calculate_attrition_rate(df, group_col)

    if chart_df.empty:
        st.warning("Không có dữ liệu phù hợp để hiển thị biểu đồ này.")
        return chart_df

    fig = px.bar(
        chart_df,
        x=group_col,
        y="AttritionRate",
        text=chart_df["AttritionRate"].round(2),
        hover_data=[
            "TotalEmployees",
            "AttritionEmployees"
        ],
        title=title,
        category_orders={
            group_col: chart_df[group_col].astype(str).tolist()
        }
    )

    fig.update_traces(
        texttemplate="%{text:.2f}%",
        textposition="outside",
        marker_color=get_bar_colors(chart_df),
        width=0.55
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
        margin=dict(l=30, r=30, t=70, b=80)
    )

    st.plotly_chart(fig, width="stretch")

    return chart_df


def show_count_bar(df, group_col, title, height=420):
    chart_df = (
        df[group_col]
        .value_counts()
        .reset_index()
    )

    chart_df.columns = [group_col, "Count"]

    fig = px.bar(
        chart_df,
        x=group_col,
        y="Count",
        text="Count",
        title=title
    )

    fig.update_traces(
        textposition="outside",
        marker_color="#457B9D",
        width=0.55
    )

    fig.update_layout(
        height=height,
        yaxis_title="Employee Count",
        xaxis_title="",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        margin=dict(l=30, r=30, t=70, b=80)
    )

    st.plotly_chart(fig, width="stretch")

    return chart_df


def create_age_group(df):
    df = df.copy()

    df["AgeGroup"] = pd.cut(
        df["Age"],
        bins=[0, 25, 35, 45, 55, 100],
        labels=[
            "Under 25",
            "25-34",
            "35-44",
            "45-54",
            "55+"
        ]
    )

    return df


def create_income_group(df):
    df = df.copy()

    df["IncomeGroup"] = pd.qcut(
        df["MonthlyIncome"],
        q=4,
        labels=[
            "Low Income",
            "Mid-Low Income",
            "Mid-High Income",
            "High Income"
        ],
        duplicates="drop"
    )

    return df


def create_years_company_group(df):
    df = df.copy()

    df["YearsAtCompanyGroup"] = pd.cut(
        df["YearsAtCompany"],
        bins=[-1, 1, 5, 10, 100],
        labels=[
            "0-1 years",
            "2-5 years",
            "6-10 years",
            "10+ years"
        ]
    )

    return df


# =========================
# SIDEBAR FILTERS
# =========================

def apply_overview_filters(df):
    st.sidebar.title("🔎 Filters")

    department_filter = st.sidebar.multiselect(
        "Department",
        options=sorted(df["Department"].dropna().unique()),
        default=sorted(df["Department"].dropna().unique())
    )

    jobrole_filter = st.sidebar.multiselect(
        "Job Role",
        options=sorted(df["JobRole"].dropna().unique()),
        default=sorted(df["JobRole"].dropna().unique())
    )

    gender_filter = st.sidebar.multiselect(
        "Gender",
        options=sorted(df["Gender"].dropna().unique()),
        default=sorted(df["Gender"].dropna().unique())
    )

    overtime_filter = st.sidebar.multiselect(
        "OverTime",
        options=sorted(df["OverTime"].dropna().unique()),
        default=sorted(df["OverTime"].dropna().unique())
    )

    age_min = int(df["Age"].min())
    age_max = int(df["Age"].max())

    age_range = st.sidebar.slider(
        "Age Range",
        min_value=age_min,
        max_value=age_max,
        value=(age_min, age_max)
    )

    filtered_df = df[
        (df["Department"].isin(department_filter)) &
        (df["JobRole"].isin(jobrole_filter)) &
        (df["Gender"].isin(gender_filter)) &
        (df["OverTime"].isin(overtime_filter)) &
        (df["Age"].between(age_range[0], age_range[1]))
    ]

    return filtered_df


# =========================
# KPI CARD
# =========================

def show_kpi_card(title, value):
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


# =========================
# PAGE 1 MAIN
# =========================

def show_overview(filtered_df):
    inject_css()

    st.subheader("Overview")

    df = prepare_attrition_flag(filtered_df)

    total_employees = len(df)

    if total_employees == 0:
        st.warning("Không có dữ liệu phù hợp với filter hiện tại.")
        return

    df = create_age_group(df)
    df = create_income_group(df)
    df = create_years_company_group(df)

    attrition_employees = int(df["AttritionFlag"].sum())
    active_employees = total_employees - attrition_employees
    attrition_rate = attrition_employees / total_employees * 100

    average_age = df["Age"].mean()
    average_income = df["MonthlyIncome"].mean()
    average_years_company = df["YearsAtCompany"].mean()
    performance_rating = df["PerformanceRating"].mean()

    # =========================
    # KPI CARDS
    # =========================

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

    st.divider()

    # =========================
    # SMALL PAGES / TABS
    # =========================

    tab1, tab2, tab3, tab4 = st.tabs([
        "Job & Department",
        "Work Conditions",
        "Demographics",
        "Income & Tenure"
    ])

    # =========================
    # TAB 1: JOB & DEPARTMENT
    # =========================

    with tab1:
        st.markdown(
            """
            <div class="insight-box">
            <b>Focus:</b> Phân tích Attrition theo phòng ban và vị trí công việc.
            Mục này giúp HR xác định nhóm công việc nào có tỷ lệ nghỉ việc cao nhất.
            </div>
            """,
            unsafe_allow_html=True
        )

        col1, col2 = st.columns([1, 1])

        with col1:
            show_attrition_bar(
                df,
                "Department",
                "Attrition Rate by Department"
            )

        with col2:
            show_count_bar(
                df,
                "Department",
                "Employee Count by Department"
            )

        show_attrition_bar(
            df,
            "JobRole",
            "Attrition Rate by Job Role",
            height=500
        )

    # =========================
    # TAB 2: WORK CONDITIONS
    # =========================

    with tab2:
        st.markdown(
            """
            <div class="insight-box">
            <b>Focus:</b> Phân tích điều kiện làm việc như overtime, business travel,
            work-life balance và job satisfaction.
            </div>
            """,
            unsafe_allow_html=True
        )

        col1, col2 = st.columns(2)

        with col1:
            show_attrition_bar(
                df,
                "OverTime",
                "Attrition Rate by OverTime"
            )

        with col2:
            show_attrition_bar(
                df,
                "BusinessTravel",
                "Attrition Rate by Business Travel"
            )

        col3, col4 = st.columns(2)

        with col3:
            show_attrition_bar(
                df,
                "WorkLifeBalance",
                "Attrition Rate by Work Life Balance"
            )

        with col4:
            show_attrition_bar(
                df,
                "JobSatisfaction",
                "Attrition Rate by Job Satisfaction"
            )

    # =========================
    # TAB 3: DEMOGRAPHICS
    # =========================

    with tab3:
        st.markdown(
            """
            <div class="insight-box">
            <b>Focus:</b> Phân tích Attrition theo nhóm tuổi, giới tính,
            tình trạng hôn nhân và lĩnh vực học vấn.
            </div>
            """,
            unsafe_allow_html=True
        )

        col1, col2 = st.columns(2)

        with col1:
            show_attrition_bar(
                df,
                "AgeGroup",
                "Attrition Rate by Age Group"
            )

        with col2:
            show_attrition_bar(
                df,
                "Gender",
                "Attrition Rate by Gender"
            )

        col3, col4 = st.columns(2)

        with col3:
            show_attrition_bar(
                df,
                "MaritalStatus",
                "Attrition Rate by Marital Status"
            )

        with col4:
            show_attrition_bar(
                df,
                "EducationField",
                "Attrition Rate by Education Field"
            )

    # =========================
    # TAB 4: INCOME & TENURE
    # =========================

    with tab4:
        st.markdown(
            """
            <div class="insight-box">
            <b>Focus:</b> Phân tích mối liên hệ giữa thu nhập, thời gian làm việc
            và khả năng nghỉ việc.
            </div>
            """,
            unsafe_allow_html=True
        )

        col1, col2 = st.columns(2)

        with col1:
            show_attrition_bar(
                df,
                "IncomeGroup",
                "Attrition Rate by Income Group"
            )

        with col2:
            show_attrition_bar(
                df,
                "YearsAtCompanyGroup",
                "Attrition Rate by Years at Company"
            )

        col3, col4 = st.columns(2)

        with col3:
            fig_income = px.box(
                df,
                x="Attrition",
                y="MonthlyIncome",
                title="Monthly Income Distribution by Attrition"
            )

            fig_income.update_layout(
                height=430,
                xaxis_title="Attrition",
                yaxis_title="Monthly Income",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)"
            )

            st.plotly_chart(fig_income, width="stretch")

        with col4:
            fig_years = px.box(
                df,
                x="Attrition",
                y="YearsAtCompany",
                title="Years at Company Distribution by Attrition"
            )

            fig_years.update_layout(
                height=430,
                xaxis_title="Attrition",
                yaxis_title="Years at Company",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)"
            )

            st.plotly_chart(fig_years, width="stretch")

    st.divider()

    with st.expander("View Filtered Data"):
        preview_columns = [
            "Age",
            "Gender",
            "Department",
            "JobRole",
            "MonthlyIncome",
            "YearsAtCompany",
            "OverTime",
            "Attrition"
        ]

        st.dataframe(
            df[preview_columns],
            width="stretch"
        )