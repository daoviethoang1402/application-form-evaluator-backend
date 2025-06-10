from app.tasks.resume_parser_tasks import extract_cv_task
from fastapi import APIRouter

router = APIRouter(prefix="/resume-parser", tags=["Resume Parser"])

@router.get("/execute/")
def execute_resume_parser(subpath: str, filename: str, required_fields: str):
    try:        
        task = extract_cv_task.delay(subpath, filename, required_fields)

        return {
            'status': 'processing',
            'message': {
                'task_id': task.id,
                'details': 'Đang trích xuất thông tin từ CV. Vui lòng chờ trong giây lát.'
            }
        }
    
    except Exception as e:
        return {
            'status': 'error',
            'message': {
                'details': str(e),
            }
        }