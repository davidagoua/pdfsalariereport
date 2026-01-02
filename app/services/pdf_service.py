
import re
import os
from pypdf import PdfReader, PdfWriter
import logging

logger = logging.getLogger(__name__)

def extract_info_from_text(text: str):
    """
    Extracts Matricule and Period from PDF text using Regex.
    """
    if not text:
        return None, None

    # Matricule Regex: Look for 'Matricule' keyword or pattern
    # Based on PDF analysis: "Matricule ... PERC001"
    # Or simpler: find "PERC\d+"
    matricule_match = re.search(r'(PERCO?\d+)', text)
    matricule = matricule_match.group(1) if matricule_match else None
    matricule = matricule.replace("O", "0")
    # Period Regex: Try to find multiple date formats
    # The layout seems to contain dates like 01/10/25 floating around.
    # Strategy: Find all dates, exclude birthdates (if any). Use the one corresponding to current month/year context or just first one found that looks like a period start.
    
    # "Période du : ... 01/10/25" (might be separated by newlines)
    # We'll just look for any date dd/mm/yy
    dates = re.findall(r'(\d{2})/(\d{2})/(\d{2})', text)
    
    month_map = {
        '01': 'JANV', '02': 'FEV', '03': 'MARS', '04': 'AVRIL', '05': 'MAI', '06': 'JUIN',
        '07': 'JUIL', '08': 'AOUT', '09': 'SEPT', '10': 'OCT', '11': 'NOV', '12': 'DEC'
    }
    
    period_str = ""
    # Heuristic: The period is usually the first or second date found in the header area.
    # In the sample: "01/10/25 31/10/25". 
    # Let's take the first date found as the "month reference".
    if dates:
        # dates[0] is ('01', '10', '25')
        month = dates[0][1]
        year = dates[0][2]
        month_name = month_map.get(month, "MOIS")
        period_str = f"{month_name}{year}"

    return matricule, period_str

def generate_filename(matricule: str, name: str, period: str) -> str:
    """
    Generates the standardized filename.
    Format: [Last 2 digits of Matricule] [Name Firstname] BULLETIN DE SALAIRE [Period]
    Example: 01 HERVE KOFFI BULLETIN DE SALAIRE SEPT25
    """
    # Last 2 digits of matricule
    digits = re.findall(r'\d+', matricule)
    last_digits = digits[-1][-2:] if digits else "00"
        
    safe_name = re.sub(r'[^a-zA-Z0-9\s]', '', name).upper()
    
    # Name Logic: "KOFFI N'GUESSAN HERVE" -> "HERVE KOFFI"
    # User wanted: "DERNINER PRENOMS" + "NOM"
    # Assessing "KOFFI N'GUESSAN HERVE":
    # Last token = HERVE (Firstname)
    # First token = KOFFI (Lastname main part)
    
    parts = safe_name.split()
    if len(parts) >= 2:
        firstname = parts[-1]
        lastname = parts[0] # Take just the first part of the lastname to be concise
        formatted_name = f"{firstname} {lastname}"
    else:
        formatted_name = safe_name

    return f"{last_digits} {formatted_name} BULLETIN DE SALAIRE {period}"

def process_pdf_splits(pdf_path: str, employee_map: dict, output_dir: str):
    """
    Splits the PDF and saves individual files based on extracted/mapped info.
    Returns a list of processed file info.
    """
    reader = PdfReader(pdf_path)
    processed_files = []
    
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        matricule, period = extract_info_from_text(text)
        
        status = "NON TROUVE"
        file_name = f"page_{i+1}.pdf"
        email = ""
        employee_name = ""
        
        if matricule and matricule in employee_map:
            emp_data = employee_map[matricule]
            employee_name = emp_data['name']
            email = emp_data['email']
            
            # Generate new filename
            new_name = generate_filename(matricule, employee_name, period)
            file_name = f"{new_name}.pdf"
            status = "TROUVE"
        
        # Save split PDF
        output_path = os.path.join(output_dir, file_name)
        writer = PdfWriter()
        writer.add_page(page)
        with open(output_path, "wb") as f:
            writer.write(f)
            
        processed_files.append({
            "id": matricule if matricule else f"UNKNOWN_{i}",
            "original_index": i,
            "name": employee_name,
            "email": email,
            "filename": file_name,
            "status": status,
            "path": output_path
        })
        
    return processed_files
