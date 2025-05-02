from fastapi import APIRouter
from app.services.utils import get_file_path, set_file_path
from app.services.jd_quantifier_service import generate_score_schema_from_jd
import os
import json

router = APIRouter(prefix="/jd-quantifier", tags=["JD Quantifier"])

@router.get("/execute")
async def execute_jd_quantifier(
    subpath: str,
    filename: str,
    scoring_scale_min: int = 1,
    scoring_scale_max: int = 5,
):
    """
    Execute JD Quantifier with the given parameters.
    """
    file_path = get_file_path(subpath, filename)
    schema = await generate_score_schema_from_jd(file_path, scoring_scale_min, scoring_scale_max)
    if not schema:
        return {"status": "error"}
    else:
        file_name, file_ext = os.path.splitext(os.path.basename(filename))
        result_path = set_file_path("results/jd_quantifier", f'[schema]{file_name}.json')
        with open(result_path, "w", encoding="utf-8") as file:
            json.dump(schema, file, ensure_ascii=False, indent=4)
        return {"status": "success", "file_path": result_path}