import pandas as pd
from src.database.connection import engine

def insert_data(df):
    try:
        # =========================
        # CLEAN DATA
        # =========================
        df = df.where(pd.notnull(df), None)

        # Standardize column names
        df.columns = df.columns.str.replace(" ", "_").str.strip().str.lower()

        df.to_sql(
            name="tickets",
            con=engine,
            if_exists="append",   # ------------------replace----------------------------
            index=False
        )

        print("Table 'tickets' created & data inserted!")

    except Exception as e:
        print("Database Insert Error:", e)