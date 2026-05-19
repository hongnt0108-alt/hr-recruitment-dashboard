from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from config import DATABASE_URL


def get_engine() -> Engine:
    return create_engine(DATABASE_URL)