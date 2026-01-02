
import pandas as pd
import sys

excel_path = "/Users/macbookpro/devspace/pdfsalarie/PC 3   EMAIL PERSONNEL PERFORMERS.xlsx"

print("--- EXCEL DEEP DIVE ---")
try:
    # Read first 10 rows without header to see layout
    df = pd.read_excel(excel_path, header=None, nrows=10)
    print(df)
except Exception as e:
    print(f"Error reading Excel: {e}")
