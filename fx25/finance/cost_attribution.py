# fx25/finance/cost_attribution.py
"""
Cost Attribution System: Track profit real por producto
- Costos: API, supplier, ads, shipping
- Revenue: Dinero que entra
- Resultado: Profit = Revenue - Total Costs
"""

from fx25.kv.sqlite_kv import get_kv_store

class CostAttribution:
    def __init__(self):
        self.kv = get_kv_store()
    
    def track_product_cost(self, product_id: str, cost: float) -> None:
        """Costo del producto (supplier)"""
        key = f"cost:{product_id}:product"
        self.kv.set(key, round(cost, 2))
    
    def track_ad_spend(self, product_id: str, spend: float) -> None:
        """Gasto en ads"""
        key = f"cost:{product_id}:ads"
        current = self.kv.get(key) or 0.0
        self.kv.set(key, round(current + spend, 2))
    
    def track_shipping_cost(self, product_id: str, cost: float) -> None:
        """Costo de shipping"""
        key = f"cost:{product_id}:shipping"
        self.kv.set(key, round(cost, 2))
    
    def track_revenue(self, product_id: str, revenue: float) -> None:
        """Revenue cuando vende"""
        key = f"revenue:{product_id}"
        current = self.kv.get(key) or 0.0
        self.kv.set(key, round(current + revenue, 2))
    
    def get_profit_summary(self, product_id: str) -> dict:
        """Calcula profit REAL"""
        revenue = self.kv.get(f"revenue:{product_id}") or 0.0
        cost_product = self.kv.get(f"cost:{product_id}:product") or 0.0
        cost_ads = self.kv.get(f"cost:{product_id}:ads") or 0.0
        cost_shipping = self.kv.get(f"cost:{product_id}:shipping") or 0.0
        
        total_cost = cost_product + cost_ads + cost_shipping
        true_profit = revenue - total_cost
        true_roas = (revenue / total_cost) if total_cost > 0 else 0
        
        return {
            "product_id": product_id,
            "revenue": round(revenue, 2),
            "cost_product": round(cost_product, 2),
            "cost_ads": round(cost_ads, 2),
            "cost_shipping": round(cost_shipping, 2),
            "total_cost": round(total_cost, 2),
            "true_profit": round(true_profit, 2),
            "true_roas": round(true_roas, 2),
        }

def get_cost_attribution() -> CostAttribution:
    return CostAttribution()
