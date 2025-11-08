# scripts/test_shopify_create_dry.py
from fx25.clients.shopify_client import ShopifyClient

if __name__ == "__main__":
    c = ShopifyClient(dry=True)
    spec = {"product": {"title": "Dry Product", "vendor": "Acme", "variants": [{"price": "19.99"}]}}
    res = c.create_product(spec, dry=True)
    print("CREATE DRY:", res.get("ok") is True, res.get("dry") is True)
