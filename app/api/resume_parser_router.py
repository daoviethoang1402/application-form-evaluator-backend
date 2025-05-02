from fastapi import APIRouter, HTTPException
import os
from app.services import resume_parser_service
from app.services.utils import get_file_path, set_file_path

import pandas as pd

router = APIRouter(prefix="/resume-parser", tags=["Resume Parser"])

@router.get("/parse-all/")
async def parse_all_resumes(subpath: str, filename: str, required_fields: str):
    file_path = get_file_path(subpath, filename)
    # if not os.path.exists(file_path):
    #     raise HTTPException(status_code=404, detail="File not found")

    # Parse resumes from sheet
    print(f"Parsing resumes from file: {file_path}")
    # Use await to ensure we wait for the parsing to complete
    output, error_list = await resume_parser_service.parse_all_resumes_from_excel(file_path, required_fields)
    
    # Create results directory for resume parser if it doesn't exist
    # output_dir = "app/storage/results/resume_parser"
    # if not os.path.exists(output_dir):
    #     os.makedirs(output_dir)

    # # Save output file to the results directory
    # result_path = os.path.join(output_dir, f"{file_name}_parsed.xlsx")
    file_name, file_ext = os.path.splitext(os.path.basename(filename))
    result_path = set_file_path("results/resume_parser", file_name + "_parsed" + file_ext)    
    try:
        output.to_excel(result_path, index=False)    
    except Exception as e:
        return {"status": "error", "message": str(e), "errors": error_list}
    else:
        return {"status": "success", "file_path": result_path, "errors": error_list}