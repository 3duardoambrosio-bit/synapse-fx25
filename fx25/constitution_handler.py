from typing import Literal, Dict

# Validador mínimo (placeholder) – aquí conectaremos tus 76 “abuelos”
ALLOWED: Dict[str, bool] = {
    "research": True,
    "design": True,
    "data_analysis": True,
    "hybrid": True,
}

def check_constitution(task_type: Literal["research","design","data_analysis","hybrid"]) -> bool:
    # Aquí después pondremos reglas reales (límites de riesgo, ética, etc.)
    return ALLOWED.get(task_type, False)
