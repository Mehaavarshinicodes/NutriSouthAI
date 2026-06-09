import pandas as pd
import os
import streamlit as st

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "dishes.csv")

@st.cache_data
def load_dishes() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    # Normalise boolean columns
    bool_cols = ["veg_flag", "is_diabetic_friendly", "is_weight_loss_friendly",
                 "oil_heavy", "contains_gluten", "contains_dairy"]
    for col in bool_cols:
        df[col] = df[col].astype(str).str.strip().str.lower() == "true"
    return df
