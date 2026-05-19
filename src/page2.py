import joblib
import pandas as pd
import streamlit as st
from train_model import train_model
from paths import MODEL_PATH


@st.cache_resource
def load_model():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Không tìm thấy model tại: {MODEL_PATH}. "
            "Hãy chạy `python src\\train_model.py` trước."
        )

    return joblib.load(MODEL_PATH)


def get_model_features(model, df):
    if hasattr(model, "feature_names_in_"):
        return list(model.feature_names_in_)

    drop_columns = [
        "Attrition",
        "AttritionFlag",
        "Attrition_clean",
        "EmployeeNumber",
        "EmployeeCount",
        "Over18",
        "StandardHours",
    ]

    return [
        col for col in df.columns
        if col not in drop_columns
    ]


def get_risk_level(probability):
    if probability < 0.3:
        return "Low"
    if probability < 0.6:
        return "Medium"
    return "High"


def show_recommendation(risk_level):
    if risk_level == "High":
        st.error("Nhân viên này có rủi ro nghỉ việc cao.")

        st.markdown(
            """
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


def build_input_form(feature_cols, df):
    input_data = {}

    col1, col2, col3 = st.columns(3)
    columns = [col1, col2, col3]

    for index, feature in enumerate(feature_cols):
        current_col = columns[index % 3]

        if feature not in df.columns:
            current_col.warning(f"Không tìm thấy cột `{feature}` trong data.")
            continue

        series = df[feature].dropna()

        if series.empty:
            current_col.warning(f"Cột `{feature}` không có dữ liệu hợp lệ.")
            continue

        with current_col:
            if series.dtype == "object":
                options = sorted(series.astype(str).unique())

                input_data[feature] = st.selectbox(
                    label=feature,
                    options=options,
                )

            elif series.nunique() <= 10:
                options = sorted(series.unique())

                input_data[feature] = st.selectbox(
                    label=feature,
                    options=options,
                )

            else:
                min_value = float(series.min())
                max_value = float(series.max())
                mean_value = float(series.mean())

                if pd.api.types.is_integer_dtype(series):
                    input_data[feature] = st.number_input(
                        label=feature,
                        min_value=int(min_value),
                        max_value=int(max_value),
                        value=int(mean_value),
                    )
                else:
                    input_data[feature] = st.number_input(
                        label=feature,
                        min_value=min_value,
                        max_value=max_value,
                        value=mean_value,
                    )

    return input_data


def show_prediction_result(model, input_data):
    input_df = pd.DataFrame([input_data])

    prediction = model.predict(input_df)[0]
    probability = model.predict_proba(input_df)[0][1]
    risk_level = get_risk_level(probability)

    st.subheader("Prediction Result")

    result_col1, result_col2, result_col3 = st.columns(3)

    result_col1.metric(
        label="Attrition Probability",
        value=f"{probability * 100:.2f}%",
    )

    result_col2.metric(
        label="Risk Level",
        value=risk_level,
    )

    result_col3.metric(
        label="Prediction",
        value="Attrition" if prediction == 1 else "No Attrition",
    )

    show_recommendation(risk_level)


def show_prediction(df):
    st.subheader("🔮 Employee Attrition Prediction")

    st.markdown(
        """
        Trang này dùng model đã train để dự báo khả năng một nhân viên có thể nghỉ việc.
        Bạn nhập thông tin nhân viên, model sẽ trả về xác suất Attrition.
        """
    )

    try:
        model = load_model()

    except FileNotFoundError:
        st.warning("Chờ chút nha người đẹp...")

        try:
            train_model()
            load_model.clear()
            model = load_model()

        except Exception as error:
            st.error("Không thể train model tự động.")
            st.info(
                "Hãy kiểm tra database đã có bảng `hr_attrition` chưa "
                "và kiểm tra DATABASE_URL trong Streamlit Secrets."
            )
            st.exception(error)
            return
    except Exception as error:
        st.error("Không thể load model.")
        st.exception(error)
        return

    feature_cols = get_model_features(model, df)

    st.info(
        f"Model đang sử dụng **{len(feature_cols)} features** để dự báo Attrition."
    )

    st.divider()

    input_data = build_input_form(feature_cols, df)

    st.divider()

    if st.button("Predict Attrition Risk", type="primary"):
        try:
            show_prediction_result(model, input_data)
        except Exception as error:
            st.error("Có lỗi khi dự báo. Kiểm tra lại input hoặc model.")
            st.exception(error)