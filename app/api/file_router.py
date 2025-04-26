# Chứa các api liên quan đến file
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from app.services import file_service

router = APIRouter()

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    return file_service.save_file(file)

@router.get("/download/")
async def download_file(filename: str):
    try:
        file_path = file_service.get_file_path(filename)
        return FileResponse(file_path, filename=filename)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/view/")
async def view_file(filename: str):
    try:
        return file_service.view_file_content(filename)
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/list")
async def list_files():
    files = file_service.list_files()
    return {"files": files}

@router.delete("/delete/")
async def delete_file(filename: str):
    try:
        file_service.delete_file(filename)
        return {"message": f"File {filename} deleted successfully"}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))