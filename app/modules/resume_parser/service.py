import requests

from app.llm.gemini_service import generate_content
from app.llm.mistral_service import extract_text_from_pdf
from .prompt import JSON_GENERATING_PROMPT, QUERY_PROMPT
from .utils import convert_to_export_link

def generate_json_schema(required_fields):
    prompt = JSON_GENERATING_PROMPT.format(required_fields=required_fields)
    return generate_content(prompt)

def extract_content(url, language="vi"):
    url = convert_to_export_link(url)
    response = requests.head(url, allow_redirects=True)
    content_type = response.headers.get('Content-Type')

    document = {
        "type": "image_url" if 'image' in content_type else "document_url",
        "image_url" if 'image' in content_type else "document_url": url,
        "language": language,
    }
    return extract_text_from_pdf(document)

def parse_resume(url, required_fields, json_schema):
    '''
    Trả về 1 string có dạng JSON. Xử lý lỗi ở resume_parser_service.py
    '''
    file_content = extract_content(url)
    if not file_content or not json_schema:
        return ""

    prompt = QUERY_PROMPT.format(
        required_fields=required_fields,
        json_schema=json_schema,
        content=file_content
    )
    response_text = generate_content(prompt)
    return response_text
