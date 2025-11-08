# scripts/test_shopify_ratelimit_stress.py
import threading, time
from fx25.clients.shopify_client import ShopifyClient

def worker(c: ShopifyClient, i: int, results: list):
    # usamos create_product DRY para ejercer el bucket
    spec = {"product": {"title": f"Stress {i}", "vendor": "Test", "variants": [{"price": "9.99"}]}}
    try:
        c.create_product(spec, dry=True)
        results.append(True)
    except Exception as e:
        print("ERR:", e)
        results.append(False)

if __name__ == "__main__":
    c = ShopifyClient(dry=True, bucket_capacity=2.0, refill_rate=2.0)
    N = 6  # llamadas totales; ~mínimo 3s con 2 req/s
    threads = []
    results = []
    t0 = time.monotonic()
    for i in range(N):
        th = threading.Thread(target=worker, args=(c, i, results), daemon=True)
        th.start()
        threads.append(th)
    for th in threads:
        th.join()
    dt = time.monotonic() - t0
    rate = N / dt if dt > 0 else 0
    print(f"CALLS={N} DURATION={dt:.2f}s RATE={rate:.2f} req/s PASS={all(results) and rate<=2.3}")
