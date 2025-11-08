# fx25/modules/go_nogo.py
from typing import Dict, Any

DEFAULT_THRESHOLDS = {
    "price_min_mx": 500,
    "price_max_mx": 1500,
    "min_margin_pct": 0.30,
    "comp_top3_min_reviews": 500,
    "comp_top3_max_rating": 4.6,   # si los top están todos en 4.9 con miles de reviews, es guerra dura
    "need_angles_min": 3
}

def evaluate_product(signals: Dict[str, Any], thresholds: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    signals esperado (ejemplos):
    {
      "avg_price_mx": 999,
      "est_margin_pct": 0.35,
      "competitors_top3": [
        {"price": 1099, "rating": 4.5, "reviews": 1200},
        {"price": 999, "rating": 4.4, "reviews": 800},
        {"price": 899, "rating": 4.6, "reviews": 650}
      ],
      "angles_count": 3
    }
    """
    t = {**DEFAULT_THRESHOLDS, **(thresholds or {})}
    reasons = []

    ok_price_band = (t["price_min_mx"] <= float(signals.get("avg_price_mx", 0)) <= t["price_max_mx"])
    if not ok_price_band:
        reasons.append("Fuera de banda de precio objetivo")

    ok_margin = float(signals.get("est_margin_pct", 0)) >= t["min_margin_pct"]
    if not ok_margin:
        reasons.append("Margen estimado insuficiente")

    comps = signals.get("competitors_top3", [])
    if len(comps) < 3:
        reasons.append("Menos de 3 competidores para referencia")
    else:
        reviews_ok = all(c.get("reviews", 0) >= t["comp_top3_min_reviews"] for c in comps)
        ratings_ok = all(float(c.get("rating", 0)) <= t["comp_top3_max_rating"] for c in comps)
        if not reviews_ok:
            reasons.append("Competidores top con pocas reseñas (señal débil)")
        if not ratings_ok:
            reasons.append("Ratings de top demasiado altos (batalla dura)")

    ok_angles = int(signals.get("angles_count", 0)) >= t["need_angles_min"]
    if not ok_angles:
        reasons.append("Menos de 3 ángulos de diferenciación")

    decision = "go" if not reasons else "hold" if len(reasons) <= 2 else "no-go"
    return {
        "decision": decision,
        "reasons": reasons,
        "thresholds": t,
        "signals_seen": signals
    }
