from mistralai import Mistral
from dotenv import load_dotenv
import os

load_dotenv()
mistral = Mistral(api_key=os.getenv('MISTRAL_API_KEY'))

def extract_text_from_pdf(document, model="mistral-ocr-latest"):
    try:
        response = mistral.ocr.process(
            model=model,
            document=document,
            include_image_base64=True
        )
    except Exception as e:
        print(f"Error when calling Mistral: {e}")
        return None
    return response.pages[0].markdown
