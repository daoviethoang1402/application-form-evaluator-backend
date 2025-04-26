import pandas as pd

def find_resume_column(sheet: pd.DataFrame) -> str:
    for col in sheet.columns:
        if sheet[col].astype(str).str.contains('https://drive.google.com', na=False).any():
            return col
    return None

def convert_to_export_link(url):
    if 'https://drive.google.com/file/d/' in url:
        file_id = url.split('/d/')[1].split('/')[0]
    elif 'open?id=' in url:
        file_id = url.split('=')[1]
    elif 'uc?id=' in url:
        file_id = url.split('=')[1]
    else:
        return url
    return f"https://drive.google.com/uc?export=download&id={file_id}"
