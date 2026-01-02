
import pandas as pd
import sys

excel_path = "/Users/macbookpro/devspace/pdfsalarie/PC 3   EMAIL PERSONNEL PERFORMERS.xlsx"

print("--- EXCEL SMART ANALYSIS ---")
try:
    xl = pd.ExcelFile(excel_path)
    print("Sheet names:", xl.sheet_names)
    
    for sheet in xl.sheet_names:
        print(f"\n--- Processing Sheet: {sheet} ---")
        df = pd.read_excel(excel_path, sheet_name=sheet)
        print("Shape:", df.shape)
        # Drop completely empty rows/cols to find the 'real' data
        df_clean = df.dropna(how='all').dropna(axis=1, how='all')
        print("Cleaned Shape:", df_clean.shape)
        if not df_clean.empty:
            print("First 5 cleaned rows:")
            print(df_clean.head())
            print("Columns found:", df_clean.columns.tolist())
except Exception as e:
    print(f"Error reading Excel: {e}")
