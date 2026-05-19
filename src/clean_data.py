import pandas as pd

df = pd.read_csv("data/raw/WA_Fn-UseC_-HR-Employee-Attrition.csv")
df = df.replace({'Attrition': {'Yes': 1, 'No': 0}})

df.to_csv("data/processed/clean_data.csv", index=False)