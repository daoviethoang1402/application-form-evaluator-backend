import sys
import os
from dotenv import load_dotenv
import posixpath
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from app.modules.jd_quantifier.service import gen_and_log_schema_from_jd
from app.worker import celery_app
from app.utils.filepath import set_file_path
import json

# Load environment variables from .env file
load_dotenv()

# Access the API keys
ATHINA_API_KEY = os.getenv('ATHINA_API_KEY')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

prompt_template_path = posixpath.join(".", "app/modules/jd_quantifier/prompt_templates", "prompt_template_v2.txt")
with open(prompt_template_path, "r", encoding="utf-8") as file:
    PROMPT_TEMPLATE = file.read().strip()
MODEL = "gemini-2.5-pro-preview-05-06"

@celery_app.task(bind=True, name='jd_quantifier.generate_schema')
def generate_schema_task(self, jd_path: str, filename: str, scoring_scale_min: int, scoring_scale_max: int):
    try:
        self.update_state(state='PROGRESS', meta={'status': 'Đang xử lý JD...'})
        schema = gen_and_log_schema_from_jd(jd_path=jd_path, 
                                            scoring_scale_min=scoring_scale_min, scoring_scale_max=scoring_scale_max,
                                            prompt_template=PROMPT_TEMPLATE,
                                            google_api_key=GOOGLE_API_KEY,
                                            athina_api_key=ATHINA_API_KEY,
                                            model=MODEL)
        file_name, file_ext = os.path.splitext(os.path.basename(filename))
        result_path = set_file_path("results/jd_quantifier", f'[schema] {file_name}.json')
        
        with open(result_path, "w", encoding="utf-8") as file:
            json.dump(schema, file, ensure_ascii=False, indent=4)
        
        return {'status': 'success', 'file_path': result_path}
    except Exception as e:
        return {"status": "error", "message": str(e)}