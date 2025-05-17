import pandas as pd
from fastapi import HTTPException

def read_sheet_from_excel(file_path):
    xls = pd.ExcelFile(file_path)
    sheets = {name: xls.parse(name) for name in xls.sheet_names}
    if len(sheets) > 1:
        raise HTTPException(
            status_code=500, 
            detail="The number of sheets in the Excel file is more than 1. Please upload an Excel file with only 1 sheet."
            )
    sheet_name, table = max(sheets.items(), key=lambda item: len(item[1]))
    return table, sheet_name

def find_resume_column(sheet: pd.DataFrame) -> str:
    for col in sheet.columns:
        if sheet[col].astype(str).str.contains('https://drive.google.com', na=False).any():
            return col
    return None