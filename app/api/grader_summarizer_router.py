from fastapi import APIRouter
from celery_once import AlreadyQueued

from app.tasks.grader_summarizer_tasks import grade_summarize_task

router = APIRouter(prefix="/grader-summarizer", tags=["Grader - Summarizer"])

@router.get("/execute/")
def execute_grader_summarizer(
    subpath: str,
    filename: str,
    jd_schema_filename: str
):
    try:
        task = grade_summarize_task.delay(subpath, filename, jd_schema_filename)
        return {
            'status': 'processing',
            'message': {
                'task_id': task.id,
                'details': 'Đang chấm điểm cho các ứng viên. Vui lòng chờ trong giây lát.'
            }
        }
    except AlreadyQueued as e:
        return {
            'status': 'error',
            'message': {
                'details': f'Task đang được xử lý. Vui lòng đợi {e.countdown} giây.'
            }
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': {
                'details': str(e),
            }
        }