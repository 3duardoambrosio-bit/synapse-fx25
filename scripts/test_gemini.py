from dotenv import load_dotenv
load_dotenv()  # carga las variables del .env

import os
import google.generativeai as genai

api_key = os.getenv("GEMINI_API_KEY")
assert api_key, "Falta GEMINI_API_KEY en .env"
genai.configure(api_key=api_key)

# Usa uno de estos modelos válidos:
model_id = "models/gemini-2.5-flash"    # rápido y barato
# model_id = "models/gemini-2.5-pro"   # más capaz

m = genai.GenerativeModel(model_id)
r = m.generate_content('Reply ONLY with JSON: {"ping":"pong"}')
print("OK:", r.text)
