from fastapi import APIRouter, UploadFile, HTTPException, Query, File 
from fastapi.responses import FileResponse
from app.services import file_service
from typing import Annotated

router = APIRouter(prefix="/file", tags=["File"])

@router.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    return file_service.save_file_from_user(file)

@router.get("/download/")
async def download_file(subpath: str, filename: str):
    try:
        file_path = file_service.get_file_location(subpath, filename)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    else:
        return FileResponse(file_path, filename=filename)

@router.get("/view/")
async def view_file(subpath: str, filename: str):
    try:
        return file_service.view_file_content(subpath, filename)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/list/")
async def list_files():
    files = file_service.list_files()
    return {"files": files}

@router.delete("/delete/")
async def delete_file(subpath: str, filename: str):
    try:
        file_service.delete_file(subpath, filename)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    else:
        return {"status": f"File {filename} deleted successfully"}
    
@router.get("/excel/get-columns/")
async def get_columns_from_excel(subpath: str, filename: str, sheet_name: str = None):
    try:
        columns, num_columns, resume_column = file_service.get_columns_from_excel(subpath, filename, sheet_name)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    else:
        return {"columns": columns, "num_columns": num_columns, "resume_column_name": resume_column}

@router.post("/excel/select-columns/")
async def remove_columns_from_excel(subpath: str, filename: str, sheet_name: str = None, columns: Annotated[list[str], Query(...)] = []):
    try:
        new_file_path = file_service.select_columns_from_excel(subpath, filename, sheet_name, columns)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    else:
        return {"status": "Columns selected successfully", "new_file_path": new_file_path}