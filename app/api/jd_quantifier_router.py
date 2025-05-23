from fastapi import APIRouter
from app.utils.filepath import get_file_path, set_file_path
from app.tasks.jd_quantifier_tasks import generate_schema_task
import os
import json
# from celery.result import AsyncResult
from app.worker import celery_app

router = APIRouter(prefix="/jd-quantifier", tags=["JD Quantifier"])

@router.get("/execute")
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
        file_path = get_file_path(subpath, filename)
        
        task = generate_schema_task.delay(file_path, filename, scoring_scale_min, scoring_scale_max)

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
    
@router.get("/status/{task_id}")
def get_task_status(task_id: str):
    """
    Lấy trạng thái của task dựa vào task_id
    """
    task_result = celery_app.AsyncResult(task_id)
    
    if task_result.state == 'PENDING':
        response = {
            'status': 'pending',
            'message': 'Task đang trong hàng đợi'
        }
    elif task_result.state == 'PROGRESS':
        response = {
            'status': 'progress',
            'message': task_result.info.get('status', '')
        }
    elif task_result.state == 'SUCCESS':
        response = task_result.result
    else:
        # Xử lý trường hợp lỗi
        response = {
            'status': 'error',
            'message': str(task_result.info) if task_result.info else 'Có lỗi xảy ra'
        }
    
    return response