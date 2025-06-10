from dotenv import load_dotenv
from celery import Celery
import os

load_dotenv()

celery_app = Celery('app',
             broker=os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
             backend=os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
             include=[
                 'app.tasks.jd_quantifier_tasks', 
                 'app.tasks.resume_parser_tasks',
                 'app.tasks.grader_summarizer_tasks'
             ])

# Additional Celery configurations
celery_app.conf.update(
    task_track_started=True,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    enable_utc=True,
    task_ignore_result=False,
    result_expires=3600,
)

# Celery Once configuration
celery_app.conf.ONCE = {
    'backend': 'celery_once.backends.Redis',
    'settings': {
        'url': os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
        'default_timeout': 3600
    },
    'unlock_before_run': False,
    'raise_on_duplicate': True,
}