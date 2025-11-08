# scripts/test_telegram_alert.py
from fx25.alerts.telegram_alert import send_telegram

if __name__ == "__main__":
    res = send_telegram("ALERTA: prueba de sistema (gasto>ingreso=STOP / producto zombie=MATA)")
    print("RESULT:", res)
