from fastapi import APIRouter

from app.worker import celery_app

router = APIRouter(prefix='/task-status', tags=["Task Status"])

@router.get("/{task_id}")
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