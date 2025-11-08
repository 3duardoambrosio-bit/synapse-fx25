# scripts/health_check_gemini.py
from fx25.config import GEMINI_MODEL_ID
from fx25.clients.gemini_client import ask_json

if __name__ == "__main__":
    # pedimos SOLO JSON con el campo health
    prompt = 'Reply ONLY with JSON: {"health":"ok"}'
    out = ask_json(GEMINI_MODEL_ID, prompt)

    print(out)  # para ver la respuesta cruda

    # reporte legible
    try:
        status = out.get("health") if isinstance(out, dict) else None
        print("HEALTH:", "OK" if status == "ok" else "FAIL")
    except Exception as e:
        print("HEALTH: FAIL (parse error)", e)
