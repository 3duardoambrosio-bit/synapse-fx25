from typing import List, Dict, Any
import re

DEFAULT_WEIGHTS = {"price":0.55, "seller":0.25, "shipping":0.10, "promo":0.10}

def _norm(v, vmin, vmax):
    if vmin is None or vmax is None or vmax<=vmin: return 0.5
    return max(0.0, min(1.0, (v - vmin) / (vmax - vmin)))

def _slug(t: str) -> str:
    t = t.lower()
    t = re.sub(r"[^a-z0-9\s\-]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t

def _dedupe(offers: List[Dict[str,Any]]) -> List[Dict[str,Any]]:
    seen = set(); out=[]
    for o in offers:
        k = (_slug(o.get("title","")), o.get("permalink"))
        if k in seen: continue
        seen.add(k); out.append(o)
    return out

def rank_offers(offers: List[Dict[str,Any]], weights: Dict[str,float] = None) -> List[Dict[str,Any]]:
    if not offers: return []
    w = {**DEFAULT_WEIGHTS, **(weights or {})}
    offers = _dedupe(offers)

    prices = [float(o.get("price") or 0) for o in offers if o.get("price") is not None]
    pmin, pmax = (min(prices), max(prices)) if prices else (None, None)

    ranked=[]
    for o in offers:
        price = float(o.get("price") or 0.0)
        price_score = 1.0 - _norm(price, pmin, pmax)  # barato = mejor
        seller = o.get("seller_score")
        seller_score = seller if isinstance(seller,(int,float)) else 0.6
        ship_score = 1.0 if o.get("shipping_free") else 0.6
        promo = 0.0
        if o.get("original_price"):
            try:
                disc = 1 - (price / float(o["original_price"]))
                promo = max(0.0, min(1.0, disc))
            except Exception:
                promo = 0.0
        score = (w["price"]*price_score + w["seller"]*seller_score +
                 w["shipping"]*ship_score + w["promo"]*promo)
        o2 = dict(o); o2["score"]=round(score,4)
        o2["score_components"]={"price":round(price_score,3),"seller":round(seller_score,3),
                                "ship":round(ship_score,3),"promo":round(promo,3)}
        ranked.append(o2)

    ranked.sort(key=lambda x:(x["score"], x.get("seller_score") or 0.0), reverse=True)
    return ranked
