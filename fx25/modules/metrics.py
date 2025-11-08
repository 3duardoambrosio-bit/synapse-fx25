# fx25/modules/metrics.py
import csv
import os
from datetime import datetime
from typing import Dict, Any

METRICS_PATH = os.path.join("outputs", "metrics.csv")
HEADER = [
    "ts", "task_type", "model_used", "ok",
    "latency_ms", "tokens_prompt", "tokens_completion", "cost_usd",
    "note"
]

def ensure_header():
    os.makedirs("outputs", exist_ok=True)
    if not os.path.exists(METRICS_PATH):
        with open(METRICS_PATH, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(HEADER)

def record_metric(row: Dict[str, Any]):
    ensure_header()
    ts = datetime.utcnow().isoformat()
    out = [
        ts,
        row.get("task_type", ""),
        row.get("model_used", ""),
        str(row.get("ok", "")),
        str(row.get("latency_ms", "")),
        str(row.get("tokens_prompt", "")),
        str(row.get("tokens_completion", "")),
        str(row.get("cost_usd", "")),
        row.get("note", ""),
    ]
    with open(METRICS_PATH, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(out)
