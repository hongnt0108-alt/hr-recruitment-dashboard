import os

from dotenv import load_dotenv

from paths import ENV_PATH


load_dotenv(ENV_PATH)

DATABASE_URL = os.getenv("DATABASE_URL")

try:
    import streamlit as st

    if not DATABASE_URL and "DATABASE_URL" in st.secrets:
        DATABASE_URL = st.secrets["DATABASE_URL"]
except Exception:
    pass

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL chưa được khai báo trong .env hoặc Streamlit Secrets."
    )