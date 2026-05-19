from pathlib import Path

import joblib
import pandas as pd
import streamlit as st


# =========================
# PATH CONFIG
# =========================

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "attrition_model.pkl"


# =========================
# LOAD MODEL
# =========================

@st.cache_resource
def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Không tìm thấy model tại: {MODEL_PATH}. "
            "Hãy chạy python src\\train_model.py trước."
        )

    model = joblib.load(MODEL_PATH)
    return model


# =========================
# HELPER FUNCTIONS
# =========================

def get_model_features(model, df):
    """
    Lấy danh sách feature mà model đã dùng khi train.
    Nếu model có feature_names_in_ thì dùng luôn.
    Nếu không có thì fallback bằng cách loại các cột không dùng để train.
    """

    if hasattr(model, "feature_names_in_"):
        return list(model.feature_names_in_)

    drop_columns = [
        "Attrition",
        "AttritionFlag",
        "Attrition_clean",
        "EmployeeNumber",
        "EmployeeCount",
        "Over18",
        "StandardHours"
    ]

    feature_cols = [
        col for col in df.columns
        if col not in drop_columns
    ]

    return feature_cols


def get_risk_level(probability):
    if probability < 0.3:
        return "Low"
    elif probability < 0.6:
        return "Medium"
    else:
        return "High"


def show_recommendation(risk_level, probability):
    if risk_level == "High":
        st.error("Nhân viên này có rủi ro nghỉ việc cao.")

        st.markdown(
            f"""
            **Recommendation:**

            - Xem xét workload và tình trạng overtime.
            - Trao đổi với quản lý trực tiếp để hiểu nguyên nhân rủi ro.
            - Review lương, phúc lợi hoặc career path nếu cần.
            - Ưu tiên nhân viên này trong chương trình retention.
            """
        )

    elif risk_level == "Medium":
        st.warning("Nhân viên này có rủi ro nghỉ việc trung bình.")

        st.markdown(
            """
            **Recommendation:**

            - Theo dõi thêm các chỉ số như satisfaction, overtime, income.
            - Có thể setup buổi check-in định kỳ với nhân viên.
            - Quan sát thay đổi trong hiệu suất hoặc mức độ gắn bó.
            """
        )

    else:
        st.success("Nhân viên này có rủi ro nghỉ việc thấp.")

        st.markdown(
            """
            **Recommendation:**

            - Tiếp tục duy trì môi trường làm việc hiện tại.
            - Theo dõi định kỳ, chưa cần can thiệp mạnh.
            """
        )


# =========================
# MAIN PAGE FUNCTION
# =========================

def show_prediction(df):
    st.subheader("🔮 Employee Attrition Prediction")

    st.markdown(
        """
        Trang này dùng model đã train để dự báo khả năng một nhân viên có thể nghỉ việc.
        Bạn nhập thông tin nhân viên, model sẽ trả về xác suất Attrition.
        """
    )

    model = load_model()
    feature_cols = get_model_features(model, df)

    st.info(
        f"Model đang sử dụng **{len(feature_cols)} features** để dự báo Attrition."
    )

    # with st.expander("Xem danh sách features model đang dùng"):
    #     st.write(feature_cols)

    st.divider()

    input_data = {}

    col1, col2, col3 = st.columns(3)

    columns = [col1, col2, col3]

    for index, feature in enumerate(feature_cols):
        current_col = columns[index % 3]

        if feature not in df.columns:
            current_col.warning(f"Không tìm thấy cột `{feature}` trong data.")
            continue

        series = df[feature].dropna()

        with current_col:
            # Categorical features
            if series.dtype == "object":
                options = sorted(series.astype(str).unique())

                input_data[feature] = st.selectbox(
                    label=feature,
                    options=options
                )

            # Numerical features có ít giá trị unique, ví dụ rating 1-4
            elif series.nunique() <= 10:
                options = sorted(series.unique())

                input_data[feature] = st.selectbox(
                    label=feature,
                    options=options
                )

            # Numerical continuous features
            else:
                min_value = float(series.min())
                max_value = float(series.max())
                mean_value = float(series.mean())

                # Nếu là int thì hiển thị number_input dạng int
                if pd.api.types.is_integer_dtype(series):
                    input_data[feature] = st.number_input(
                        label=feature,
                        min_value=int(min_value),
                        max_value=int(max_value),
                        value=int(mean_value)
                    )
                else:
                    input_data[feature] = st.number_input(
                        label=feature,
                        min_value=min_value,
                        max_value=max_value,
                        value=mean_value
                    )

    st.divider()

    if st.button("Predict Attrition Risk", type="primary"):
        input_df = pd.DataFrame([input_data])

        try:
            prediction = model.predict(input_df)[0]
            probability = model.predict_proba(input_df)[0][1]

            risk_level = get_risk_level(probability)

            st.subheader("Prediction Result")

            result_col1, result_col2, result_col3 = st.columns(3)

            result_col1.metric(
                label="Attrition Probability",
                value=f"{probability * 100:.2f}%"
            )

            result_col2.metric(
                label="Risk Level",
                value=risk_level
            )

            result_col3.metric(
                label="Prediction",
                value="Attrition" if prediction == 1 else "No Attrition"
            )

            show_recommendation(risk_level, probability)

        except Exception as e:
            st.error("Có lỗi khi dự báo. Kiểm tra lại input hoặc model.")
            st.exception(e)