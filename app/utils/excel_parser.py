
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def parse_excel(file_path: str) -> dict:
    """
    Parses the Excel file to create a mapping of Matricule -> {name, email}.
    Target Sheet: "EMAIL SALAIRE "
    Columns: "MATRICULE", "NOM ET PERENOM ", "EMAIL"
    """
    try:
        # Load specific sheet
        df = pd.read_excel(file_path, sheet_name="EMAIL SALAIRE ")
        
        # Clean column names (strip whitespace)
        df.columns = df.columns.str.strip()
        
        # Ensure required columns exist
        required_columns = ["MATRICULE", "NOM ET PERENOM", "EMAIL"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            # Fallback for slight variations if needed, or raise error
            logger.error(f"Missing columns: {missing_columns}")
            # Try to match loosely if exact match unsuccessful
            # Re-read with loose matching logic if critical
            raise ValueError(f"Missing columns in Excel: {missing_columns}")

        employee_map = {}
        for _, row in df.iterrows():
            matricule = str(row["MATRICULE"]).strip()
            name = str(row["NOM ET PERENOM"]).strip()
            email = str(row["EMAIL"]).strip()
            
            # Skip invalid rows
            if pd.isna(matricule) or matricule == "nan":
                continue
                
            employee_map[matricule] = {
                "name": name,
                "email": email
            }
            
        return employee_map

    except Exception as e:
        logger.error(f"Failed to parse Excel: {e}")
        raise e
