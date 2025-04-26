import pandas as pd
import os
from fastapi import UploadFile
from fastapi.responses import FileResponse
from starlette.responses import JSONResponse, Response

STORAGE_DIR = "app/storage/"
storage_mapping = {
    "UPLOAD": "uploads/",
}
# Tạo thư mục nếu chưa có
os.makedirs(STORAGE_DIR, exist_ok=True)

def read_all_sheets_from_excel(filepath, sheet_name=None):
    xls = pd.ExcelFile(filepath)
    if sheet_name is None:
        print("Finding the longest sheet...")
        sheets = {name: xls.parse(name) for name in xls.sheet_names}
        return max(sheets.items(), key=lambda item: len(item[1]))
    else:
        return xls.parse(sheet_name)

def save_file(file: UploadFile):
    file_location = os.path.join(STORAGE_DIR + storage_mapping['UPLOAD'], file.filename)
    with open(file_location, "wb+") as f:
        f.write(file.file.read())
    return {"filename": file.filename, "message": "Upload successful"}

def get_file_path(filename: str):
    file_path = os.path.join(STORAGE_DIR, filename)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File '{filename}' not found")
    return file_path

def list_files():
    result = []
    for root, dirs, files in os.walk(STORAGE_DIR):
        for name in files:
            result.append(os.path.relpath(os.path.join(root, name), STORAGE_DIR))
        for name in dirs:
            result.append(os.path.relpath(os.path.join(root, name), STORAGE_DIR))
    return result

def delete_file(filename: str):
    file_path = get_file_path(filename)
    os.remove(file_path)

def view_file_content(filename: str):
    file_path = get_file_path(filename)
    file_ext = os.path.splitext(filename)[1].lower()

    if file_ext in [".pdf", ".jpg", ".jpeg", ".png"]:
        return FileResponse(file_path)
    elif file_ext in [".xlsx", ".xls"]:
        # Chuyển về attachment để client tải xuống preview
        return FileResponse(file_path, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        # Hoặc preview dạng text nếu cần
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        return JSONResponse(content={"filename": filename, "content": content[:500]})  # chỉ trả về 500 ký tự đầu

# if __name__ == "__main__":
#     file_path = get_file_path("results/resume_parser/haha.xlsx")
#     print(file_path)
#     print(os.path.exists(file_path))