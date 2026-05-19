import os

from dotenv import load_dotenv

from paths import ENV_PATH


load_dotenv(ENV_PATH)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL chưa được khai báo trong file .env")