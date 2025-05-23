from app.tasks.jd_quantifier_tasks import generate_schema_task
from fastapi import APIRouter

router = APIRouter(prefix="/jd-quantifier", tags=["JD Quantifier"])

@router.get("/execute/")
def execute_jd_quantifier(
    subpath: str,
    filename: str,
    scoring_scale_min: int = 1,
    scoring_scale_max: int = 5,
):
    """
    Execute JD Quantifier with the given parameters.
    """
    try:        
        task = generate_schema_task.delay(subpath, filename, scoring_scale_min, scoring_scale_max)

        return {
            'status': 'processing',
            'task_id': task.id,
            'message': 'Đang xử lý JD. Vui lòng chờ trong giây lát.'
        }
    
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }