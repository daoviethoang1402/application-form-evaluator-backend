import sys
import os
# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.modules.resume_parser.utils import find_resume_column
from app.services.resume_parser_service import parse_all_resumes_from_excel
from app.services.file_service import read_all_sheets_from_excel
import pandas as pd

if __name__ == "__main__": # Testing only.
    EXAMPLE_EXCEL_TABLE = 'app/storage/uploads/test_data.xlsx'
    EXAMPLE_REQUIRED_FIELDS = "học vấn; ngoại khóa"
    OUTPUT_FILE = 'app/storage/results/resume_parser/test_data_parsed.xlsx'
    SHEET_NAME = 'Form Responses 1'
    '''
    1. Đọc file Excel
    2. Tìm cột chứa link resume
    3. Trích xuất các trường.
    Lấy các trường cần được trích xuất từ cột resume này. Đưa chúng vào 1 DataFrame
    4. Ghép DataFrame mới này vào DataFrame cũ
    5. Xuất ra file Excel mới
    '''
    sheet = read_all_sheets_from_excel(EXAMPLE_EXCEL_TABLE, sheet_name=SHEET_NAME)
    print(f"Reading '{SHEET_NAME}' from '{EXAMPLE_EXCEL_TABLE}'")
    print(f"Sheet contains {len(sheet)} rows and {len(sheet.columns)} columns")
    resume_column = find_resume_column(sheet)
    if resume_column is not None:
        print(f"Found resume column: {resume_column}")
    else:
        print("No column containing resume links found.")
        exit()

    resume_extracted_columns = parse_all_resumes_from_excel(sheet, EXAMPLE_REQUIRED_FIELDS, print_progress=True)

    # Merge the sheet DataFrame with resume_extracted_columns DataFrame
    # Since both DataFrames share the same index, we can use concat with axis=1
    combined_df = pd.concat([sheet, resume_extracted_columns], axis=1)

    # Check for duplicate columns (which can happen if column names overlap)
    duplicate_columns = combined_df.columns.duplicated()
    if any(duplicate_columns):
        print(f"Warning: Found {duplicate_columns.sum()} duplicate column(s)")
        # Keep only the first occurrence of each column name
        combined_df = combined_df.loc[:, ~duplicate_columns]

    # Save the combined DataFrame to a new Excel file
    combined_df.to_excel(OUTPUT_FILE, index=False)

    print(f"Combined data saved to {OUTPUT_FILE}")
    # # Display the first few rows of the combined DataFrame
    # combined_df.head(2)