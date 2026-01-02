
import sys
import os
import shutil

# Add project root to path
sys.path.append("/Users/macbookpro/devspace/pdfsalarie")

from app.utils.excel_parser import parse_excel
from app.services.pdf_service import process_pdf_splits

EXCEL_PATH = "/Users/macbookpro/devspace/pdfsalarie/PC 3   EMAIL PERSONNEL PERFORMERS.xlsx"
PDF_PATH = "/Users/macbookpro/devspace/pdfsalarie/PC   1  BULLETINS OCTOBRE 2025 PERFORMERS.PDF"
OUTPUT_DIR = "/Users/macbookpro/devspace/pdfsalarie/assets/test_output"

if os.path.exists(OUTPUT_DIR):
    shutil.rmtree(OUTPUT_DIR)
os.makedirs(OUTPUT_DIR)

print("--- STARTING VERIFICATION ---")

# 1. Parse Excel
print("\n[1] Parsing Excel...")
try:
    employee_map = parse_excel(EXCEL_PATH)
    print(f"SUCCESS: Loaded {len(employee_map)} employees.")
    # Print sample
    sample_key = list(employee_map.keys())[0]
    print(f"Sample: {sample_key} -> {employee_map[sample_key]}")
except Exception as e:
    print(f"FAILED Excel Parsing: {e}")
    sys.exit(1)

# 2. Process PDF
print("\n[2] Processing PDF...")
try:
    results = process_pdf_splits(PDF_PATH, employee_map, OUTPUT_DIR)
    print(f"SUCCESS: Processed {len(results)} pages.")
    
    matched_count = sum(1 for r in results if r['status'] == 'MATCHED')
    print(f"Matched: {matched_count}/{len(results)}")
    
    # Check first result
    if results:
        print("\nFirst Page Result:")
        print(results[0])
        
except Exception as e:
    print(f"FAILED PDF Processing: {e}")
    sys.exit(1)

print("\n--- VERIFICATION COMPLETE ---")
