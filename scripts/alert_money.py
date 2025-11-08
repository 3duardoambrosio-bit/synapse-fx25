# scripts/alert_money.py
import json
from fx25.alerts.telegram_alert import send_telegram

# --- SIMULACIÓN RÁPIDA (modifica estos números para probar) ---
gasto_ads = 500       # MXN gastado hoy
ingreso_ventas = 200  # MXN vendido hoy
visitas_48h = 320     # visitas últimas 48h
ventas_48h  = 1       # ventas últimas 48h
# ---------------------------------------------------------------

def main():
    eventos = []
    # Regla 1: pierdes dinero
    if ingreso_ventas < gasto_ads:
        eventos.append(("STOP", f"PÉRDIDA: gastaste {gasto_ads} y vendiste {ingreso_ventas}"))

    # Regla 2: producto zombie
    conv = (ventas_48h/visitas_48h)*100 if visitas_48h else 0.0
    if visitas_48h >= 300 and conv < 0.6:
        eventos.append(("MATA", f"ZOMBIE: {visitas_48h} visitas / {ventas_48h} ventas (conv={conv:.2f}%)"))

    if not eventos:
        print(json.dumps({"status":"OK","message":"sin alertas"} , ensure_ascii=False))
        return

    for tipo, msg in eventos:
        send_telegram(f"[{tipo}] {msg}")

    print(json.dumps({"status":"ALERT","eventos":[e[0] for e in eventos]}, ensure_ascii=False))

if __name__ == "__main__":
    main()
