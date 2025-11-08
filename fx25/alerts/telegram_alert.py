# fx25/alerts/telegram_alert.py
import os, json, urllib.request, urllib.parse

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID")
DRY_RUN   = os.getenv("DRY_RUN", "1")  # "1" = no manda, solo imprime

def send_telegram(message: str) -> dict:
    payload = {"message": message, "dry": DRY_RUN == "1"}
    if DRY_RUN == "1" or not BOT_TOKEN or not CHAT_ID:
        print("[DRY] telegram:", json.dumps(payload, ensure_ascii=False))
        return {"ok": True, "dry": True}

    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = urllib.parse.urlencode({"chat_id": CHAT_ID, "text": message}).encode()
        with urllib.request.urlopen(urllib.request.Request(url, data=data, method="POST"), timeout=10) as r:
            return {"ok": True, "dry": False, "status": r.status}
    except Exception as e:
        return {"ok": False, "error": str(e)}
