from app.tasks.grader_summarizer_tasks import grade_summarize_task
from fastapi import APIRouter

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
            'task_id': task.id,
            'message': 'Đang chấm điểm cho các ứng viên. Vui lòng chờ trong giây lát.'
        }
    
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }