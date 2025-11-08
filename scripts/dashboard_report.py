# scripts/dashboard_report.py
"""
Dashboard Integrado: Muestra Cost Attribution + Lifecycle + Recomendaciones
Ejecuta: python -m scripts.dashboard_report
"""

from fx25.finance.cost_attribution import get_cost_attribution
from fx25.products.lifecycle import get_lifecycle
from fx25.clients.shopify_client import ShopifyClient
import time

def print_header(title):
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def dashboard_report():
    """Genera reporte integrado"""
    
    print_header("🎯 DISRUPTOR PHASE 2 DASHBOARD")
    
    ca = get_cost_attribution()
    lc = get_lifecycle()
    client = ShopifyClient()
    
    # Simular productos
    products = [
        {"id": "prod1", "name": "Wireless Earbuds", "sales": 25, "cost": 50, "revenue": 150},
        {"id": "prod2", "name": "Phone Stand", "sales": 3, "cost": 10, "revenue": 35},
        {"id": "prod3", "name": "USB Cable", "sales": 0, "cost": 2, "revenue": 0},
    ]
    
    # Registrar datos
    for p in products:
        ca.track_product_cost(p["id"], p["cost"])
        ca.track_revenue(p["id"], p["revenue"])
        lc.track_sales(p["id"], p["sales"])
    
    # Imprimir tabla
    print("\n📊 PRODUCT SUMMARY:\n")
    print(f"{'Product':<20} {'State':<12} {'Revenue':<10} {'Profit':<10} {'ROAS':<8} {'Action':<25}")
    print("-" * 100)
    
    total_revenue = 0
    total_profit = 0
    
    for p in products:
        profit_data = ca.get_profit_summary(p["id"])
        state = lc.get_state(p["id"])
        action = lc.recommend_action(p["id"])
        
        total_revenue += profit_data["revenue"]
        total_profit += profit_data["true_profit"]
        
        print(f"{p['name']:<20} {state.value:<12} ${profit_data['revenue']:<9.2f} ${profit_data['true_profit']:<9.2f} {profit_data['true_roas']:<8.2f} {action[:25]:<25}")
    
    print("-" * 100)
    print(f"{'TOTAL':<20} {'':<12} ${total_revenue:<9.2f} ${total_profit:<9.2f}")
    
    # Métricas del sistema
    print_header("⚙️ SYSTEM METRICS")
    
    print(f"✅ Rate Limit: {client.bucket_remaining:.2f} req/s")
    print(f"✅ Circuit Breaker: {client.circuit_state}")
    print(f"✅ Mode: DRY (Testing)")
    
    print_header("🎯 GO/NO-GO SIGNAL")
    
    if total_profit > 0 and client.circuit_state == "CLOSED":
        print("🟢 GO - Sistema listo para vender")
    else:
        print("🔴 NO-GO - Revisar problemas")


if __name__ == "__main__":
    dashboard_report()
