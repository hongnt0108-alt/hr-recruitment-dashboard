import streamlit as st

from page1 import calculate_attrition_rate, prepare_attrition_flag


def show_key_insights(df):
    st.subheader("Key Insight Summary")

    df = prepare_attrition_flag(df)

    department_df = calculate_attrition_rate(df, "Department")
    jobrole_df = calculate_attrition_rate(df, "JobRole")
    overtime_df = calculate_attrition_rate(df, "OverTime")
    travel_df = calculate_attrition_rate(df, "BusinessTravel")

    if (
        department_df.empty
        or jobrole_df.empty
        or overtime_df.empty
        or travel_df.empty
    ):
        st.warning("Không đủ dữ liệu để tạo Key Insight Summary.")
        return

    top_department = department_df.iloc[0]
    top_jobrole = jobrole_df.iloc[0]
    top_overtime = overtime_df.iloc[0]
    top_travel = travel_df.iloc[0]

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            f"""
            **1. Department có attrition cao nhất**

            `{top_department["Department"]}` có tỷ lệ nghỉ việc khoảng  
            **{top_department["AttritionRate"]:.2f}%**.
            """
        )

        st.markdown(
            f"""
            **2. Job Role có attrition cao nhất**

            `{top_jobrole["JobRole"]}` có tỷ lệ nghỉ việc khoảng  
            **{top_jobrole["AttritionRate"]:.2f}%**.
            """
        )

    with col2:
        st.markdown(
            f"""
            **3. OverTime đáng chú ý nhất**

            Nhóm `{top_overtime["OverTime"]}` có tỷ lệ nghỉ việc khoảng  
            **{top_overtime["AttritionRate"]:.2f}%**.
            """
        )

        st.markdown(
            f"""
            **4. Business Travel đáng chú ý**

            Nhóm `{top_travel["BusinessTravel"]}` có tỷ lệ nghỉ việc khoảng  
            **{top_travel["AttritionRate"]:.2f}%**.
            """
        )

    st.info(
        """
        Các insight này là phân tích mô tả dựa trên tỷ lệ Attrition theo từng nhóm.
        Đây chưa phải là kết luận nhân quả. Để đánh giá yếu tố nào ảnh hưởng mạnh nhất
        đến dự báo, nên kết hợp thêm Feature Importance hoặc SHAP từ model.
        """
    )
