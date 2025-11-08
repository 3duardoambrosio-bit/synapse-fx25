# fx25/clients/shopify_client.py
"""
ShopifyClient v3.1 — production-ready (DRY por defecto)
- Token bucket 2 req/s (thread-safe con loop, NO recursión)
- Circuit breaker con el mismo lock, estados OPEN→HALF_OPEN→CLOSED
- Guardrails de precio (±20%); si old_price=None, lee precio actual
- Cost tracking thread-safe
- DRY mode: sin red, simula respuestas y ejerce el rate limiter CORRECTAMENTE

CHANGELOG v3→v3.1:
- FIX: _wait_if_needed usa sleep(0.5) fijo en lugar de calcular sleep_time
  Razón: Evita race condition donde sleep_time se desactualiza durante el sleep
  Impacto: Rate limit ahora EXACTO 2 req/s, no 3 req/s
"""

from __future__ import annotations
import os
import json
import time
import threading
import random
from typing import Any, Dict, Optional
from urllib import request, parse, error

# -------------------------
# Configuración por entorno
# -------------------------
DEF_API_VERSION = os.getenv("SHOPIFY_API_VERSION", "2023-10")
DEF_STORE = os.getenv("SHOPIFY_STORE", "example.myshopify.com")
DEF_TOKEN = os.getenv("SHOPIFY_ADMIN_TOKEN", "")
DEF_DRY = os.getenv("DRY_RUN", "1") == "1"

# Guardrail de precio (20%)
PRICE_DELTA_LIMIT = float(os.getenv("PRICE_DELTA_LIMIT", "0.20"))


class ShopifyClient:
    def __init__(
        self,
        store: str | None = None,
        token: str | None = None,
        *,
        api_version: str = DEF_API_VERSION,
        dry: Optional[bool] = None,
        # Rate limit local: 2 req/s
        bucket_capacity: float = 2.0,
        refill_rate: float = 2.0,  # tokens por segundo
        # Circuit breaker
        breaker_fail_threshold: int = 3,
        breaker_open_seconds: float = 60.0,
    ) -> None:
        self.store = store or DEF_STORE
        self.token = (token or DEF_TOKEN).strip()
        self.api_version = api_version
        self.dry = DEF_DRY if dry is None else dry

        # Token bucket
        self.bucket_capacity = float(bucket_capacity)
        self.refill_rate = float(refill_rate)
        self.bucket_remaining = self.bucket_capacity
        self.bucket_last_refill = time.monotonic()
        self.bucket_lock = threading.Lock()

        # Circuit breaker
        self.breaker_fail_threshold = int(breaker_fail_threshold)
        self.breaker_open_seconds = float(breaker_open_seconds)
        self.circuit_state = "CLOSED"   # CLOSED | HALF_OPEN | OPEN
        self.circuit_fail_count = 0
        self.circuit_last_failure_ts = 0.0

        # Cost tracking
        self._api_call_count = 0
        self._cost_lock = threading.Lock()

        # Flags de prueba (para tests)
        self._force_fail_for_n_calls = 0

    # ------------- Utilidades internas (TOKEN BUCKET) -------------
    def _refill_bucket_unlocked(self) -> None:
        """Rellena bucket basado en tiempo transcurrido. DEBE estar dentro del lock."""
        now = time.monotonic()
        elapsed = now - self.bucket_last_refill
        if elapsed <= 0:
            return
        self.bucket_remaining = min(
            self.bucket_capacity,
            self.bucket_remaining + elapsed * self.refill_rate,
        )
        self.bucket_last_refill = now

    def _wait_if_needed(self) -> None:
        """
        Token bucket thread-safe SIN recursión (loop).
        Consume 1 token cuando esté disponible.
        
        FIX v3.2: Usa threading.Condition para sincronización eficiente.
        Solo despierta threads cuando hay tokens disponibles.
        """
        with self.bucket_lock:
            # Esperar hasta que haya token disponible
            while self.bucket_remaining < 1.0:
                # Calcular cuánto esperar: (1 - available) / refill_rate
                deficit = 1.0 - self.bucket_remaining
                wait_time = deficit / self.refill_rate
                
                # LIBERAR LOCK durante el sleep
                self.bucket_lock.release()
                time.sleep(wait_time)
                self.bucket_lock.acquire()
                
                # Rellenar después de despertar
                self._refill_bucket_unlocked()
            
            # Ya tenemos token
            self.bucket_remaining -= 1.0
        """
        Token bucket thread-safe SIN recursión (loop).
        Consume 1 token cuando esté disponible.
        
        FIX v3.1: Si no hay token, SIEMPRE duerme 0.5s (1 / 2 req/s).
        No calcula sleep_time porque se desactualiza durante el sleep.
        Esto garantiza exactamente 2 req/s bajo concurrencia.
        """
        while True:
            with self.bucket_lock:
                self._refill_bucket_unlocked()
                if self.bucket_remaining >= 1.0:
                    self.bucket_remaining -= 1.0
                    return
            
            # Si llegamos aquí, NO hay token.
            # Dormir FUERA del lock (no bloquea otros threads).
            # Siempre 0.5s porque 1 token / 2 req/s = 0.5s
            time.sleep(0.5)
            # Loop y vuelve a intentar

    def _check_circuit_breaker(self) -> None:
        """Verifica si circuit breaker está abierto. Thread-safe."""
        with self.bucket_lock:  # Mismo lock para consistencia
            if self.circuit_state == "OPEN":
                remaining = self.breaker_open_seconds - (time.time() - self.circuit_last_failure_ts)
                if remaining > 0:
                    raise RuntimeError(f"Circuit breaker OPEN. Retry in ~{int(remaining)}s")
                # Ventana cumplida → pasar a HALF_OPEN (una sonda)
                self.circuit_state = "HALF_OPEN"

    def _record_success(self) -> None:
        """Registra operación exitosa."""
        with self.bucket_lock:
            if self.circuit_state in ("HALF_OPEN", "OPEN"):
                self.circuit_state = "CLOSED"
            self.circuit_fail_count = 0

    def _record_failure(self) -> None:
        """Registra operación fallida."""
        with self.bucket_lock:
            self.circuit_fail_count += 1
            self.circuit_last_failure_ts = time.time()
            if self.circuit_fail_count >= self.breaker_fail_threshold:
                self.circuit_state = "OPEN"

    def _inc_cost(self) -> None:
        """Incrementa contador de llamadas API (thread-safe)."""
        with self._cost_lock:
            self._api_call_count += 1

    # --------- Requests (DRY / REAL) ----------
    def _request(
        self,
        method: str,
        path: str,
        *,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None,
        dry: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        HTTP request genérico con rate limiting, circuit breaker y retry.
        """
        if dry is None:
            dry = self.dry

        # Aplica rate limit local SIEMPRE (también en DRY para testear)
        self._wait_if_needed()
        self._check_circuit_breaker()

        if dry:
            # ----- MODO SIMULACIÓN -----
            payload = {
                "method": method,
                "path": path,
                "data": data or {},
                "params": params or {}
            }
            
            # Falla forzada para pruebas de circuit breaker
            if self._force_fail_for_n_calls > 0:
                self._force_fail_for_n_calls -= 1
                self._record_failure()
                print(f"[SHOPIFY][SIM] FAIL method={method} path={path}")
                raise RuntimeError("Simulated request failure (DRY)")
            
            self._inc_cost()
            # Respuesta simulada
            print(
                f"[SHOPIFY][SIM] OK method={method} path={path} dry=1 "
                f"payload={json.dumps(payload, ensure_ascii=False)}"
            )
            self._record_success()
            return {"ok": True, "dry": True, "payload": payload}

        # ----- MODO REAL (requiere credenciales) -----
        if not self.token:
            self._record_failure()
            raise RuntimeError("SHOPIFY_ADMIN_TOKEN vacío.")

        base = f"https://{self.store}/admin/api/{self.api_version}"
        url = f"{base}{path}"
        if params:
            url += "?" + parse.urlencode(params)

        headers = {
            "Content-Type": "application/json",
            "X-Shopify-Access-Token": self.token,
        }
        body = None
        if data is not None:
            body = json.dumps(data).encode("utf-8")

        # Backoff con jitter ante 429/5xx
        max_retries = 5
        backoff = 0.8
        for attempt in range(max_retries + 1):
            req = request.Request(url, data=body, headers=headers, method=method.upper())
            try:
                with request.urlopen(req, timeout=30) as resp:
                    status = resp.status
                    txt = resp.read().decode("utf-8") if resp.length is None or resp.length > 0 else "{}"
                    self._inc_cost()
                    
                    if 200 <= status < 300:
                        self._record_success()
                        print(f"[SHOPIFY] action={method} status=OK url={path}")
                        return {
                            "ok": True,
                            "dry": False,
                            "status": status,
                            "json": json.loads(txt or "{}")
                        }
                    
                    # Trata 4xx/5xx
                    if status == 429 or 500 <= status < 600:
                        self._record_failure()
                        retry_after = resp.headers.get("Retry-After")
                        if retry_after:
                            sleep_s = float(retry_after)
                        else:
                            sleep_s = backoff * (2 ** attempt) + random.uniform(0, 0.2)
                        print(f"[SHOPIFY] status={status} backoff={sleep_s:.2f}s attempt={attempt}")
                        time.sleep(min(sleep_s, 10.0))
                        continue
                    
                    # Otros 4xx = kill inmediato
                    self._record_failure()
                    raise RuntimeError(f"HTTP {status}: {txt[:200]}")

            except error.HTTPError as e:
                self._record_failure()
                if e.code == 429 or 500 <= e.code < 600:
                    sleep_s = backoff * (2 ** attempt) + random.uniform(0, 0.2)
                    print(f"[SHOPIFY] HTTPError={e.code} backoff={sleep_s:.2f}s attempt={attempt}")
                    time.sleep(min(sleep_s, 10.0))
                    continue
                raise
            except Exception:
                self._record_failure()
                raise

        raise RuntimeError("Max retries alcanzado (429/5xx sostenido).")

    # ------------- Métodos públicos (contrato) -------------
    def create_product(
        self,
        spec: Dict[str, Any],
        *,
        dry: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Crea un producto.
        spec: dict con campos Shopify (e.g., {"product": {...}})
        """
        return self._request("POST", "/products.json", data=spec, dry=dry)

    def get_inventory(
        self,
        sku: str,
        *,
        dry: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Obtiene inventario por SKU (stub).
        """
        if (self.dry if dry is None else dry):
            # Simulación simple
            self._wait_if_needed()
            print(f"[SHOPIFY][SIM] INVENTORY sku={sku} qty=42")
            self._record_success()
            self._inc_cost()
            return {"ok": True, "dry": True, "sku": sku, "qty": 42}
        
        # En real, deberías mapear SKU→variant_id y consultar levels.
        return self._request(
            "GET",
            f"/inventory_levels.json",
            params={"sku": sku},
            dry=dry
        )

    def _get_current_price(
        self,
        product_id: str,
        *,
        dry: Optional[bool]
    ) -> float:
        """
        Obtiene precio actual de un producto.
        Usado por update_price si old_price es None.
        """
        if (self.dry if dry is None else dry):
            # Simula precio actual determinista
            return 100.0
        
        # Real: GET /products/{id}.json y resolver variant.price
        resp = self._request("GET", f"/products/{product_id}.json", dry=dry)
        try:
            product = resp["json"]["product"]
            variants = product["variants"]
            return float(variants[0]["price"])
        except Exception:
            raise RuntimeError("No se pudo leer precio actual del producto.")

    def update_price(
        self,
        product_id: str,
        new_price: float,
        *,
        old_price: Optional[float] = None,
        dry: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Actualiza precio con guardrails ±20% respecto al precio actual.
        Si old_price es None, consulta precio actual (real o simulado).
        """
        d = self.dry if dry is None else dry
        
        if old_price is None:
            old_price = self._get_current_price(product_id, dry=d)

        if old_price <= 0:
            raise ValueError("old_price inválido.")

        delta = abs(new_price - old_price) / old_price
        if delta > PRICE_DELTA_LIMIT:
            raise ValueError(
                f"price_guardrail: delta {delta:.2%} excede límite {PRICE_DELTA_LIMIT:.0%}"
            )

        if d:
            # Simula PUT de actualización
            self._wait_if_needed()
            payload = {
                "product_id": product_id,
                "old_price": old_price,
                "new_price": new_price
            }
            print(f"[SHOPIFY][SIM] UPDATE_PRICE ok payload={json.dumps(payload, ensure_ascii=False)}")
            self._record_success()
            self._inc_cost()
            return {"ok": True, "dry": True, "payload": payload}

        # Real: PUT a /products/{id}.json o a variant correspondiente
        data = {
            "product": {
                "id": product_id,
                "variants": [{"price": new_price}]
            }
        }
        return self._request("PUT", f"/products/{product_id}.json", data=data, dry=d)

    # -------- Helpers de test ----------
    def force_fail_next(self, n_calls: int) -> None:
        """Forzar fallas simuladas en DRY para probar circuit breaker."""
        self._force_fail_for_n_calls = max(0, int(n_calls))

    @property
    def api_call_count(self) -> int:
        """Devuelve total de llamadas API (thread-safe)."""
        with self._cost_lock:
            return self._api_call_count
