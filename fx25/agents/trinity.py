# fx25/agents/trinity.py

import json
import time
from typing import Literal
from fx25.config import (
    GEMINI_MODEL_ID,
    COST_CAP_PER_TASK_USD,
)
from fx25.clients.gemini_client import ask_text, ask_json

Format = Literal["plain", "bullets", "haiku", "json"]

def _make_prompt(task: str, fmt: Format, lang: str) -> str:
    base = f"""You are Trinity, a helpful assistant. Reply in {lang}.
Task: {task}."""

    if fmt == "bullets":
        return base + "\nFormat: 5 concise bullet points."
    if fmt == "haiku":
        return base + "\nFormat: a single haiku."
    if fmt == "json":
        return base + '\nReply ONLY with JSON matching: {"resumen": "..."}'
    return base + "\nFormat: brief answer."

def _rough_cost_estimate_usd(output_chars: int) -> float:
    # Estimador grosero para no pasarnos (ajústalo si quieres)
    # ~1k chars ~ 250 tokens; $0.35 / 1M tokens => costo insignificante en flash
    tokens = max(1, output_chars // 4)
    return tokens * 0.35 / 1_000_000.0

def run_trinity(task: str, lang: str = "es", fmt: Format = "plain"):
    prompt = _make_prompt(task, fmt, lang)

    t0 = time.time()
    if fmt == "json":
        out = ask_json(GEMINI_MODEL_ID, prompt)
        text_len = len(json.dumps(out, ensure_ascii=False)) if isinstance(out, (dict, list)) else len(str(out))
    else:
        out = ask_text(GEMINI_MODEL_ID, prompt)
        text_len = len(out)

    # chequeo de “presupuesto” por tarea (estimado)
    usd = _rough_cost_estimate_usd(text_len)
    if usd > COST_CAP_PER_TASK_USD:
        return {
            "error": "cost_cap_exceeded",
            "estimated_usd": round(usd, 6),
            "cap_usd": COST_CAP_PER_TASK_USD,
        }

    return out
