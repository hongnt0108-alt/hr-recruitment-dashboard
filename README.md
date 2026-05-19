# HR Attrition Project

## Overview

This project analyzes employee attrition data and builds a machine learning model to predict whether an employee is likely to leave the company.

The project includes:

- Data cleaning
- Exploratory data analysis
- Machine learning model training
- Streamlit dashboard
- Database upload scripts

## Project Structure

```text
hr-attrition-project/
├── data/
│   ├── raw/
│   │   └── .gitkeep
│   └── processed/
│       └── .gitkeep
├── models/
│   └── .gitkeep
├── notebooks/
├── src/
│   ├── clean_data.py
│   ├── config.py
│   ├── db.py
│   ├── download_data.py
│   ├── page1.py
│   ├── page2.py
│   ├── page3.py
│   ├── streamlit_app.py
│   ├── train_model.py
│   └── upload_data.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md