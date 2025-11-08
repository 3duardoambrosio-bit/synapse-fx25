import os, json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
ENV = ROOT / ".env"

required_env = [
    "SHOPIFY_STORE",
    "SHOPIFY_ADMIN_TOKEN",
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_CHAT_ID",
    "DRY_RUN",
]

def mask(v: str) -> str:
    if not v: return ""
    if len(v) <= 6: return "*" * len(v)
    return v[:3] + "…" + v[-3:]

def load_env_file(path: pathlib.Path):
    # carga .env si no está en variables del proceso
    if not path.exists(): return
    for line in path.read_text(encoding="utf-8").splitlines():
        line=line.strip()
        if not line or line.startswith("#") or "=" not in line: 
            continue
        k,v = line.split("=",1)
        os.environ.setdefault(k.strip(), v.strip())

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    load_env_file(ENV)

    checks = {}
    for k in required_env:
        val = os.environ.get(k, "")
        checks[k] = {"present": bool(val), "preview": mask(val)}

    all_ok = all(x["present"] for x in checks.values())
    status = {
        "all_ok": all_ok,
        "outputs_dir": str(OUT),
        "checks": checks,
    }
    path = OUT / "preflight.json"
    path.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(status, ensure_ascii=False))
    sys.exit(0 if all_ok else 1)

if __name__ == "__main__":
    main()
