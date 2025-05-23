from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

# Cấu hình Celery với Redis làm broker và backend
celery_app = Celery('app',
             broker=os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
             backend=os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
             include=['app.tasks.jd_quantifier_tasks'])

# Cấu hình tùy chọn
celery_app.conf.update(
    result_expires=3600,  # Kết quả hết hạn sau 1 giờ
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Ho_Chi_Minh',
    enable_utc=True,
)

# if __name__ == '__main__':
#     app.start()