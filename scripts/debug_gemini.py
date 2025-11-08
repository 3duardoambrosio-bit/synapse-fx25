import os, sys
import google.generativeai as genai

API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    print("❌ No encuentro GEMINI_API_KEY/GOOGLE_API_KEY en el entorno.")
    sys.exit(1)

genai.configure(api_key=API_KEY)

# Candidatos (con y sin 'models/') y versiones que suelen estar siempre
CANDIDATES = [
    "models/gemini-2.5-flash", "gemini-2.5-flash",
    "models/gemini-2.0-flash", "gemini-2.0-flash",
]

def ok_model(name: str) -> bool:
    try:
        m = genai.GenerativeModel(name)
        r = m.generate_content("Reply with JSON only: {\"ping\":\"pong\"}")
        print(f"✅ {name} -> {r.text}")
        return True
    except Exception as e:
        print(f"⚠️  {name} -> {type(e).__name__}: {e}")
        return False

# 1) Probar candidatos
for name in CANDIDATES:
    if ok_model(name):
        print(f"\n👉 Usa este model_id en tu config: {name}\n")
        sys.exit(0)

# 2) Si todos fallan, listar lo que tu cuenta soporta con generateContent
print("\nNingún candidato funcionó. Modelos disponibles con generateContent:")
for m in genai.list_models():
    if "generateContent" in getattr(m, "supported_generation_methods", []):
        print(" -", m.name, m.supported_generation_methods)
