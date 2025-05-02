import sys

sys.path.append('..')

from app.modules.jd_quantifier.service import gen_and_log_schema_from_jd
import posixpath

jd_path = posixpath.join(".", "data", "raw", "test_jd", "VEO - JD DIGITAL MARKETING COLLABORATOR 2025 (PART-TIME) .txt")
google_api_key_path = posixpath.join(".", "secret_keys", "gemini_api_key.txt")
athina_api_key_path = posixpath.join(".", "secret_keys", "athina_api_key.txt")

with open(google_api_key_path, "r", encoding="utf-8") as file:
    google_api_key = file.read().strip()
    
with open(athina_api_key_path, "r", encoding="utf-8") as file:
    athina_api_key = file.read().strip()
    
prompt_template_path = posixpath.join(".", "prompt_templates", "prompt_template_v2.txt")

with open(prompt_template_path, "r", encoding="utf-8") as file:
    prompt_template = file.read().strip()

schema = gen_and_log_schema_from_jd(jd_path=jd_path,
                                    scoring_scale_min=1,
                                    scoring_scale_max=5,
                                    google_api_key=google_api_key,
                                    model="gemini-2.5-pro-exp-03-25",
                                    prompt_template=prompt_template,
                                    athina_api_key=athina_api_key)

print("Schema:\n", schema)
import json
with open("schema.json", "w", encoding="utf-8") as file:
    json.dump(schema, file, ensure_ascii=False, indent=4)
print("Schema saved to schema.json")