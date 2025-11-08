# scripts/test_shopify_price_guardrails.py
from fx25.clients.shopify_client import ShopifyClient

if __name__ == "__main__":
    c = ShopifyClient(dry=True)
    product_id = "123"

    # old_price se simula 100 cuando None → delta 50% → debe bloquear
    try:
        c.update_price(product_id, new_price=50.0, old_price=None, dry=True)
        print("FAIL: guardrail no bloqueó cambio extremo")
    except ValueError as e:
        print("PASS guardrail:", str(e))

    # cambio aceptable (10%) → pasa
    ok = c.update_price(product_id, new_price=110.0, old_price=None, dry=True)
    print("OK small change:", ok.get("ok") is True)
