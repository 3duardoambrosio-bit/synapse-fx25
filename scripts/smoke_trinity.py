# scripts/smoke_trinity.py
from fx25.config import GEMINI_MODEL_ID
from fx25.clients.gemini_client import ask_json

if __name__ == "__main__":
    prompt = 'Reply ONLY with JSON: {"ping":"pong"}'
    out = ask_json(GEMINI_MODEL_ID, prompt)
    print("SMOKE JSON:", out)
