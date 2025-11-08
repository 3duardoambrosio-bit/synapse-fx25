# fx25/config.py — v0.5.1 (smoke-safe + compat)

# === Modo test ===
TEST_MODE = True            # Simula éxito si el proveedor falla (para tests)
BUDGET_GUARD_OFF = True     # No corta por presupuesto en smoke/tests

# === Conectores habilitados ===
ENABLE_CONNECTORS = {
    "gemini": True,
    "openai": False,       # placeholders para smoke
    "perplexity": False,
}

# === Modelos ===
GEMINI_MODEL_ID = "models/gemini-2.0-flash"
DEFAULT_MODELS = {
    "gemini": GEMINI_MODEL_ID,
    "openai": "gpt-4o-mini",            # placeholder
    "perplexity": "sonar-small-online", # placeholder
}

# === Defaults de generación ===
GEN_TEMPERATURE = 0.4
GEN_MAX_OUTPUT_TOKENS = 2048

# === Presupuesto / tiempos (nuevo esquema) ===
COST_CAP_PER_TASK = 0.0      # 0 => sin límite (tests)
LATENCY_BUDGET_MS = 0
MAX_CALLS_PER_TASK = 0

# === Aliases de compatibilidad (legacy) ===
COST_CAP_PER_TASK_USD = COST_CAP_PER_TASK
TIMEOUT_SEC = 45
RETRIES = 2

# === Costos por proveedor (0 en tests para no “exceder”) ===
PROVIDER_COSTS = {
    "gemini": {"prompt_per_1k": 0.0, "completion_per_1k": 0.0},
    "openai": {"prompt_per_1k": 0.0, "completion_per_1k": 0.0},
    "perplexity": {"prompt_per_1k": 0.0, "completion_per_1k": 0.0},
}

# === Rutas / logging ===
DATA_PATH = "./data"
OUTPUT_PATH = "./outputs"
LOG_FILE = f"{OUTPUT_PATH}/fx25.log"
