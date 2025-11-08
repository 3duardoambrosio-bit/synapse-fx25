import json, os, time
from typing import Any, Dict

LINEAGE_FILE = "./outputs/lineage.log"

def record_decision(entry: Dict[str, Any]) -> None:
    os.makedirs("./outputs", exist_ok=True)
    entry = {"ts": time.time(), **entry}
    with open(LINEAGE_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
