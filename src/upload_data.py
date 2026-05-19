import pandas as pd
from sqlalchemy import create_engine
from config import DATABASE_URL

df = pd.read_csv("data/processed/clean_data.csv")

engine = create_engine(DATABASE_URL)

df.to_sql(
    "hr_attrition",
    engine,
    if_exists="replace",
    index=False
)

print("Uploaded successfully")