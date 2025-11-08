# test_gemini_min.py
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.environ.get("GOOGLE_API_KEY")
assert api_key, "No encontré GOOGLE_API_KEY en el .env"
genai.configure(api_key=api_key)

# OJO: Usa un modelo que esté en tu lista (vimos "gemini-2.5-flash")
model = genai.GenerativeModel("gemini-2.5-flash")

resp = model.generate_content('Reply ONLY with JSON: {"ping":"pong"}')
print(resp.text)
