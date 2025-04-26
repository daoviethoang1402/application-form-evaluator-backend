from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
from app.services import resume_parser_service
import pandas as pd

router = APIRouter(prefix="/resume-parser", tags=["Resume Parser"])

@router.get("/parse-all/")
async def parse_all_resumes(filename: str, required_fields: str):
    # Create storage directory if it doesn't exist
    storage_dir = "app/storage/uploads"
    file_path = os.path.join(storage_dir, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    # Parse resumes from sheet
    print(f"Parsing resumes from file: {file_path}")
    # Use await to ensure we wait for the parsing to complete
    output, error_list = await resume_parser_service.parse_all_resumes_from_excel(file_path, required_fields)
    # Create results directory if it doesn't exist
    results_dir = "app/storage/results/resume_parser"
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)

    # Save output file to the results directory
    file_name, file_extension = os.path.splitext(filename)
    result_path = os.path.join(results_dir, f"{file_name}_parsed.xlsx")
    try:
        output.to_excel(result_path, index=False)    
    except Exception as e:
        return {"status": "error", "message": str(e)}
    else:
        return {"status": "success", "file_path": result_path, "errors": error_list}