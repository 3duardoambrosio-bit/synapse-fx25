import os
import json
import logging
from datetime import datetime
from typing import Any, Dict

# ---------- Logging ----------
_LOGGER = None

def get_logger() -> logging.Logger:
    global _LOGGER
    if _LOGGER:
        return _LOGGER
    logger = logging.getLogger("synapse_fx25")
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
        logger.addHandler(ch)
    _LOGGER = logger
    return logger

# ---------- Utilidades de archivos ----------
def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)

def timestamp_id() -> str:
    # Ej: 2025-10-24_23-07-15
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def save_json(filepath: str, data: Dict[str, Any]) -> None:
    ensure_dir(os.path.dirname(filepath))
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
