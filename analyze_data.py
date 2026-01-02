
import pandas as pd
from pypdf import PdfReader
import sys

excel_path = "/Users/macbookpro/devspace/pdfsalarie/PC 3   EMAIL PERSONNEL PERFORMERS.xlsx"
pdf_path = "/Users/macbookpro/devspace/pdfsalarie/PC   1  BULLETINS OCTOBRE 2025 PERFORMERS.PDF"

print("--- EXCEL ANALYSIS ---")
try:
    df = pd.read_excel(excel_path)
    print("Columns:", df.columns.tolist())
    print("First row:", df.iloc[0].to_dict())
except Exception as e:
    print(f"Error reading Excel: {e}")

print("\n--- PDF ANALYSIS ---")
try:
    reader = PdfReader(pdf_path)
    page = reader.pages[0]
    text = page.extract_text()
    print("Page 0 Text Preview:")
    print(text[:1000]) # Print first 1000 chars
except Exception as e:
    print(f"Error reading PDF: {e}")
