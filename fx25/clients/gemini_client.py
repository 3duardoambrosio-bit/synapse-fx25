# fx25/clients/gemini_client.py

from typing import Any, Dict
import time
import google.generativeai as genai
from fx25.config import (
    GEMINI_MODEL_ID,
    TIMEOUT_SEC,
    RETRIES,
    GEN_TEMPERATURE,
    GEN_MAX_OUTPUT_TOKENS,
)

def _build_model(model_id: str | None = None):
    mid = model_id or GEMINI_MODEL_ID
    m = genai.GenerativeModel(
        mid,
        generation_config={
            "temperature": GEN_TEMPERATURE,
            "max_output_tokens": GEN_MAX_OUTPUT_TOKENS,
        },
    )
    return m

def _call_with_retries(fn, *args, **kwargs):
    last = None
    for i in range(RETRIES + 1):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            last = e
            # backoff muy simple
            time.sleep(0.6 * (i + 1))
    raise RuntimeError(f"[Gemini] Falló tras {RETRIES+1} intentos: {last}")

def ask_text(model_id: str, prompt: str) -> str:
    try:
        m = _build_model(model_id)
        resp = _call_with_retries(
            m.generate_content, prompt, request_options={"timeout": TIMEOUT_SEC}
        )
        return resp.text or ""
    except Exception as e:
        raise RuntimeError(f"[Gemini] generate_content falló: {e}")

def ask_json(model_id: str, json_prompt: str) -> Dict[str, Any] | Any:
    """
    Te pasas un prompt tipo: 'Reply ONLY with JSON: {"ping":"pong"}'
    Si regresa JSON válido, lo intentamos parsear; si no, devolvemos texto.
    """
    out = ask_text(model_id, json_prompt)
    # intento de parseo seguro
    try:
        import json
        return json.loads(out)
    except Exception:
        return out
