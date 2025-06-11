import os
from typing import Annotated

from fastapi.responses import FileResponse
from fastapi import APIRouter, UploadFile, HTTPException, Query, File 

from app.utils import excel as excel
from app.utils import filepath as path

router = APIRouter(prefix="/file", tags=["File"])

@router.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    file_location = path.set_file_path(subpath="responses/", filename=file.filename)
    with open(file_location, "wb+") as f:
        f.write(file.file.read())
    if not file.filename.endswith(('.xlsx', '.xls')):
        return {
            'status': 'success',
            'message': {
                'file_path': file.filename
            }
        }
    try:
        ## Only for checking if the file has more than one sheet
        table, name = excel.read_sheet_from_excel(file_location)
    except Exception as e:
        os.remove(file_location)
        raise HTTPException(status_code=500, detail=str(e))
    else:
        return {
            'status': 'success',
            'message': {
                'file_path': file.filename
            }
        }

@router.get("/download/")
async def download_file(subpath: str, filename: str):
    try:
        file_path = path.get_file_path(subpath, filename)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    else:
        return FileResponse(file_path, filename=filename)

@router.delete("/delete/")
async def delete_file(subpath: str, filename: str):
    try:
        file_path = path.get_file_path(subpath, filename)
        os.remove(file_path)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    else:
        return {
            'status': 'success',
            'message': 'File {filename} deleted successfully'
        }

@router.get("/list/")
async def list_files():
    files_tree = path.build_folder_tree()
    return {
        'status': 'success',
        'message': {
            'files_tree': files_tree
        }
    }
    
@router.get("/excel-get-columns/")
async def get_columns_from_excel(subpath: str, filename: str):
    try:
        # Lấy table từ filename
        file_path = path.get_file_path(subpath, filename)
        table, name = excel.read_sheet_from_excel(file_path)
        resume_column = excel.find_resume_column(table)

        # Lấy tên các cột trong table
        columns = table.columns.tolist()
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    else:
        return {
            'status': 'success',
            'message': {
                'num_columns': len(columns), 
                'columns': columns, 
                'resume_column_name': resume_column
            }
        }

@router.post("/excel-select-columns/")
async def select_columns(subpath: str, filename: str, columns: Annotated[list[str], Query(...)] = []):
    try:
         # Lấy table từ filename
        file_path = path.get_file_path(subpath, filename)
        table, name = excel.read_sheet_from_excel(file_path)

        # Giữ các cột được chỉ định trong table
        if columns:
            table = table[columns]
        
        # Lưu table vào file mới
        file_name, file_ext = os.path.splitext(filename)
        new_file_path = path.set_file_path(subpath, file_name + "_filtered" + file_ext)
        table.to_excel(new_file_path, index=False)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    else:
        return {
            'status': 'success',
            'message': {
                'file_path': new_file_path
            }
        }