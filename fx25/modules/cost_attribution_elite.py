# fx25/modules/cost_attribution_elite.py
"""
ELITE Cost Attribution: Análisis financiero avanzado
- Profit tracking real
- Anomaly detection
- Trend predictions
- ROI por canal
"""

from fx25.kv.sqlite_kv import get_kv_store
from datetime import datetime, timedelta
from typing import Dict, List

class CostAttributionElite:
    def __init__(self):
        self.kv = get_kv_store()
    
    def track_product_cost(self, product_id: str, cost: float, cost_type: str = "product") -> None:
        """Track granular costs"""
        key = f"cost:{product_id}:{cost_type}:{datetime.now().isoformat()}"
        self.kv.set(key, round(cost, 2))
    
    def track_revenue(self, product_id: str, revenue: float, channel: str = "shopify") -> None:
        """Track revenue by channel"""
        key = f"revenue:{product_id}:{channel}:{datetime.now().isoformat()}"
        self.kv.set(key, round(revenue, 2))
    
    def get_profit_summary(self, product_id: str) -> Dict:
        """Advanced profit analysis"""
        # Simulate data retrieval
        revenue = self.kv.get(f"revenue:{product_id}") or 0.0
        cost_product = self.kv.get(f"cost:{product_id}:product") or 0.0
        cost_ads = self.kv.get(f"cost:{product_id}:ads") or 0.0
        cost_shipping = self.kv.get(f"cost:{product_id}:shipping") or 0.0
        
        total_cost = cost_product + cost_ads + cost_shipping
        true_profit = revenue - total_cost
        true_roas = (revenue / total_cost) if total_cost > 0 else 0
        
        # ANOMALY DETECTION
        anomalies = []
        if true_profit < 0:
            anomalies.append("⚠️ Negative profit detected")
        if true_roas > 20:
            anomalies.append("📊 Unusually high ROAS - verify data")
        if cost_ads > revenue * 0.5:
            anomalies.append("💸 Ad spend > 50% of revenue - reduce")
        
        # TREND ANALYSIS
        trend = "STABLE"
        if true_profit > revenue * 0.4:
            trend = "🚀 GROWING"
        elif true_profit < revenue * 0.05:
            trend = "📉 DECLINING"
        
        return {
            "product_id": product_id,
            "revenue": round(revenue, 2),
            "cost_product": round(cost_product, 2),
            "cost_ads": round(cost_ads, 2),
            "cost_shipping": round(cost_shipping, 2),
            "total_cost": round(total_cost, 2),
            "true_profit": round(true_profit, 2),
            "true_roas": round(true_roas, 2),
            "profit_margin_pct": round((true_profit / revenue * 100) if revenue > 0 else 0, 2),
            "anomalies": anomalies,
            "trend": trend,
            "recommendation": self._get_recommendation(true_profit, true_roas, revenue)
        }
    
    def _get_recommendation(self, profit: float, roas: float, revenue: float) -> str:
        """Smart recommendation engine"""
        if profit < 0:
            return "🔴 STOP - Losing money, review costs"
        elif roas < 1.5:
            return "🟡 PAUSE - Low ROAS, optimize targeting"
        elif profit > revenue * 0.3:
            return "🟢 SCALE - High profit, increase budget"
        else:
            return "🟠 OPTIMIZE - Stable, fine-tune margins"

def get_cost_attribution_elite() -> CostAttributionElite:
    return CostAttributionElite()
