import os

from dotenv import load_dotenv

from paths import ENV_PATH


# Load biến môi trường từ file .env
load_dotenv(ENV_PATH)


def get_database_url() -> str:
    """
    Lấy DATABASE_URL từ .env trước.
    Nếu không có thì lấy từ Streamlit Secrets.
    """

    database_url = os.getenv("DATABASE_URL")

    if database_url:
        return database_url

    try:
        import streamlit as st

        if "DATABASE_URL" in st.secrets:
            return st.secrets["DATABASE_URL"]

    except Exception:
        pass

    raise ValueError(
        "DATABASE_URL chưa được khai báo trong file .env hoặc Streamlit Secrets."
    )


DATABASE_URL = get_database_url()