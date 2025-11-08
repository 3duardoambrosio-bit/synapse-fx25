# scripts/test_shopify_circuit_breaker.py
import time
from fx25.clients.shopify_client import ShopifyClient

if __name__ == "__main__":
    # reducimos ventana para test rápido
    c = ShopifyClient(dry=True, breaker_fail_threshold=3, breaker_open_seconds=2.0)

    # Forzar 3 fallas consecutivas → OPEN
    c.force_fail_next(3)
    failed = 0
    for _ in range(3):
        try:
            c.create_product({"product": {"title": "X"}}, dry=True)
        except Exception as e:
            failed += 1
            print("FAIL as expected:", str(e)[:80])

    print("failed:", failed, "state=OPEN expected")
    try:
        c.create_product({"product": {"title": "will_block"}}, dry=True)
    except Exception as e:
        print("OPEN block:", str(e)[:80])

    # Esperar a HALF_OPEN
    time.sleep(2.1)
    # Primer intento en HALF_OPEN: éxito → CLOSE
    res = c.create_product({"product": {"title": "probe"}}, dry=True)
    print("probe ok:", bool(res.get("ok")), "breaker should CLOSE now")
