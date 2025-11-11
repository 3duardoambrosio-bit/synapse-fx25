import os, time, logging, requests
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

log = logging.getLogger("buyer.meli")
ML_SITE = os.getenv("ML_SITE", "MLM")  # México
BASE = "https://api.mercadolibre.com"

def _session() -> requests.Session:
    s = requests.Session()
    retry = Retry(
        total=5, connect=3, read=3, backoff_factor=0.4,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        raise_on_status=False,
    )
    s.mount("https://", HTTPAdapter(max_retries=retry))
    s.headers.update({"User-Agent":"fx25-buyer/1.0"})
    return s

@dataclass
class Offer:
    source: str
    id: str
    title: str
    price: float
    original_price: Optional[float]
    permalink: Optional[str]
    currency: Optional[str]
    seller_id: Optional[int]
    seller_score: Optional[float]
    shipping_free: bool

def _seller_score(level_id: Optional[str]) -> float:
    # Mapeo estable; default neutral 0.6
    table = {"5_green":0.95,"4_light_green":0.85,"3_yellow":0.65,"2_orange":0.45,"1_red":0.25}
    return table.get(level_id or "", 0.60)

def _throttle(i:int): 
    if i: time.sleep(0.25)  # ~4 req/s

def search_meli(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    s = _session()
    r = s.get(f"{BASE}/sites/{ML_SITE}/search", params={"q":query, "limit":min(50,limit)}, timeout=10)
    r.raise_for_status()
    raw = r.json().get("results", [])
    out: List[Offer] = []
    for i, it in enumerate(raw):
        _throttle(i)
        offer = Offer(
            source="mercadolibre",
            id=str(it.get("id")),
            title=it.get("title") or "",
            price=float(it.get("price") or 0.0),
            original_price=float(it["original_price"]) if it.get("original_price") else None,
            permalink=it.get("permalink"),
            currency=it.get("currency_id"),
            seller_id=it.get("seller",{}).get("id"),
            seller_score=None,
            shipping_free=bool(it.get("shipping",{}).get("free_shipping")),
        )
        out.append(offer)

    # enrich seller reputation (best-effort)
    for i, o in enumerate(out):
        if not o.seller_id: 
            o.seller_score = None
            continue
        _throttle(i)
        try:
            sr = s.get(f"{BASE}/users/{o.seller_id}", timeout=10)
            if sr.ok:
                rep = sr.json().get("seller_reputation",{}) or {}
                o.seller_score = _seller_score(rep.get("level_id"))
            else:
                log.warning("seller %s reputation http=%s", o.seller_id, sr.status_code)
        except Exception as e:
            log.warning("seller %s reputation error=%s", o.seller_id, e)
            o.seller_score = None

    # convertir a dicts serializables
    return [asdict(x) for x in out]
