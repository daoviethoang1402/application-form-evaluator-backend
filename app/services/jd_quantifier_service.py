import sys
import os
from dotenv import load_dotenv
import posixpath
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from app.modules.jd_quantifier.service import gen_and_log_schema_from_jd

# Load environment variables from .env file
load_dotenv()

# Access the API keys
ATHINA_API_KEY = os.getenv('ATHINA_API_KEY')
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

prompt_template_path = posixpath.join(".", "app/modules/jd_quantifier/prompt_templates", "prompt_template_v2.txt")
with open(prompt_template_path, "r", encoding="utf-8") as file:
    PROMPT_TEMPLATE = file.read().strip()
MODEL = "gemini-2.5-pro-preview-03-25"

async def generate_score_schema_from_jd(jd_path: str, scoring_scale_min: int, scoring_scale_max: int):
    schema = gen_and_log_schema_from_jd(jd_path=jd_path, 
                                        scoring_scale_min=scoring_scale_min, scoring_scale_max=scoring_scale_max,
                                        prompt_template=PROMPT_TEMPLATE,
                                        google_api_key=GOOGLE_API_KEY,
                                        athina_api_key=ATHINA_API_KEY,
                                        model=MODEL)
    return schema