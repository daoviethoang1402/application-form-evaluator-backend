from google import genai
from dotenv import load_dotenv
import os

load_dotenv()
gemini = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))

def generate_content(prompt, model="gemini-2.0-flash"):
    try:
        response = gemini.models.generate_content(
            model=model,
            contents=[prompt]
        )
    except Exception as e:
        print(f"Error when calling Gemini: {e}")
        return None
    return response.candidates[0].content.parts[0].text
