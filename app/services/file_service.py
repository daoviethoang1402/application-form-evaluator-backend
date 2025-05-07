import pandas as pd
import os
from fastapi import UploadFile
from fastapi.responses import FileResponse
from starlette.responses import JSONResponse
from .utils import get_file_path, set_file_path, STORAGE_DIR
from app.modules.resume_parser.utils import find_resume_column

def save_file_from_user(file: UploadFile):
    file_location = set_file_path(subpath="uploads/", filename=file.filename)
    with open(file_location, "wb+") as f:
        f.write(file.file.read())
    return {"filename": file.filename, "message": "Upload successful"}

def get_file_location(subpath: str, filename: str):
    return get_file_path(subpath, filename)

def list_files():
    result = []
    for root, dirs, files in os.walk(STORAGE_DIR):
        for name in files:
            result.append(os.path.relpath(os.path.join(root, name), STORAGE_DIR))
        for name in dirs:
            result.append(os.path.relpath(os.path.join(root, name), STORAGE_DIR))
    return result

def delete_file(subpath: str, filename: str):
    file_path = get_file_path(subpath, filename)
    os.remove(file_path)

def view_file_content(subpath: str, filename: str):
    file_path = get_file_path(subpath, filename)
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

def read_sheet_from_excel(file_path, sheet_name=None):
    xls = pd.ExcelFile(file_path)
    if sheet_name is None:
        print("Return the responses sheet by finding the longest sheet...")
        sheets = {name: xls.parse(name) for name in xls.sheet_names}
        sheet_name, table = max(sheets.items(), key=lambda item: len(item[1]))
        return sheet_name, table
    else:
        print(f"Return the responses sheet by name: {sheet_name}")
        table = xls.parse(sheet_name)
        return table
    
def get_columns_from_excel(subpath, filename, sheet_name=None, return_resume_column=True):
    # Lấy table từ filename
    file_path = get_file_path(subpath, filename)
    _, table = read_sheet_from_excel(file_path, sheet_name)
    resume_column = find_resume_column(table)

    # Lấy tên các cột trong table
    columns = table.columns.tolist()
    return columns, len(columns), resume_column if return_resume_column else None

def select_columns_from_excel(subpath, filename, sheet_name=None, columns=[]):
    # Lấy table từ filename
    file_path = get_file_path(subpath, filename)
    _, table = read_sheet_from_excel(file_path, sheet_name)

    # Giữ các cột được chỉ định trong table
    if columns:
        table = table[columns]
    
    # Lưu table vào file mới
    file_name, file_ext = os.path.splitext(filename)
    new_file_path = set_file_path(subpath, file_name + "_modified" + file_ext)
    table.to_excel(new_file_path, index=False)
    return new_file_path