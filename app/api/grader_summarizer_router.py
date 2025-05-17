from fastapi import APIRouter
import json
import os
from app.utils.filepath import get_file_path, set_file_path
from app.utils.excel import read_sheet_from_excel
from app.services.grader_summarizer_service import grade_and_summarize_candidates

router = APIRouter(prefix="/grader-summarizer", tags=["Grader - Summarizer"])

@router.get("/evaluate-all")
async def evaluate_all_candidates(
    subpath: str,
    filename: str,
    jd_schema_filename: str
):
    excel_file_path = get_file_path(subpath, filename)
    jd_schema_file_path = get_file_path('results/jd_quantifier/', jd_schema_filename)

    table, name = read_sheet_from_excel(excel_file_path)
    with open(jd_schema_file_path, "r") as f:
        grading_schema = json.load(f)
    
    result_df = await grade_and_summarize_candidates(table, grading_schema)

    file_name, file_ext = os.path.splitext(os.path.basename(filename))
    result_path = set_file_path("results/grader_summarizer", file_name + "_graded" + file_ext)    
    try:
        result_df.to_excel(result_path, index=False)    
    except Exception as e:
        return {"status": "error", "message": str(e)}
    else:
        return {"status": "success", "file_path": result_path}