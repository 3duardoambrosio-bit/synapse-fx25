# scripts/smoke_connectors.py
from fx25.config import DEFAULT_MODELS
from fx25.clients.gemini_client import ask_text

def log(ok, provider, model, msg=""):
    status = "ok=True" if ok else "ok=False"
    extra = f" | {msg}" if msg else ""
    print(f"[{provider.upper()}] model={model} {status}{extra}")

if __name__ == "__main__":
    # OPENAI (placeholder: solo imprime que está activo)
    log(True, "openai", DEFAULT_MODELS["openai"], "ping simulated")

    # PERPLEXITY (placeholder)
    log(True, "perplexity", DEFAULT_MODELS["perplexity"], "ping simulated")

    # GEMINI (real)
    try:
        txt = ask_text(DEFAULT_MODELS["gemini"], 'Reply ONLY with JSON: {"ping":"pong"}')
        ok = '"ping":"pong"' in txt.replace(" ", "")
        log(ok, "gemini", DEFAULT_MODELS["gemini"], txt[:120])
    except Exception as e:
        log(False, "gemini", DEFAULT_MODELS["gemini"], f"error={e}")
