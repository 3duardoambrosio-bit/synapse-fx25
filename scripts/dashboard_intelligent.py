# scripts/dashboard_intelligent.py
"""
Dashboard Inteligente: Scores de módulos + Recomendaciones personalizadas
Ejecuta: python -m scripts.dashboard_intelligent
"""

from fx25.finance.cost_attribution import get_cost_attribution
from fx25.products.lifecycle import get_lifecycle
from fx25.clients.shopify_client import ShopifyClient
from fx25.modules.module_scorer import get_module_scorer

def print_header(title):
    print("\n" + "="*70)
    print(f" {title}")
    print("="*70)

def dashboard_intelligent():
    """Dashboard con decisiones inteligentes"""
    
    print_header("🧠 DISRUPTOR INTELLIGENT DASHBOARD - PHASE 3")
    
    ca = get_cost_attribution()
    lc = get_lifecycle()
    client = ShopifyClient()
    scorer = get_module_scorer()
    
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
    
    # PRODUCTS TABLE
    print("\n📊 PRODUCT SUMMARY:\n")
    print(f"{'Product':<20} {'State':<12} {'Revenue':<10} {'Profit':<10} {'ROAS':<8}")
    print("-" * 70)
    
    total_revenue = 0
    total_profit = 0
    zombie_count = 0
    decay_count = 0
    growth_count = 0
    
    for p in products:
        profit_data = ca.get_profit_summary(p["id"])
        state = lc.get_state(p["id"])
        
        total_revenue += profit_data["revenue"]
        total_profit += profit_data["true_profit"]
        
        if state.value == "ZOMBIE":
            zombie_count += 1
        elif state.value == "DECAY":
            decay_count += 1
        elif state.value == "GROWTH":
            growth_count += 1
        
        print(f"{p['name']:<20} {state.value:<12} ${profit_data['revenue']:<9.2f} ${profit_data['true_profit']:<9.2f} {profit_data['true_roas']:<8.2f}")
    
    print("-" * 70)
    print(f"{'TOTAL':<20} {'':<12} ${total_revenue:<9.2f} ${total_profit:<9.2f}")
    
    # MODULE SCORES
    print_header("🎯 MODULE INTELLIGENT SCORES")
    
    # Score Shopify
    shopify_score = scorer.score_shopify_client(client.bucket_remaining, client.circuit_state)
    print(f"\n{shopify_score.name}: {shopify_score.score}/10 {shopify_score.health.value}")
    if shopify_score.deficiencies:
        print(f"  ❌ Deficiencies: {', '.join(shopify_score.deficiencies)}")
    if shopify_score.recommendations:
        for rec in shopify_score.recommendations:
            print(f"  ✅ {rec}")
    
    # Score Finance
    avg_roas = (total_revenue / total_profit) if total_profit > 0 else 0
    finance_score = scorer.score_finance(total_profit, total_revenue, avg_roas)
    print(f"\n{finance_score.name}: {finance_score.score}/10 {finance_score.health.value}")
    if finance_score.deficiencies:
        print(f"  ❌ Deficiencies: {', '.join(finance_score.deficiencies)}")
    if finance_score.recommendations:
        for rec in finance_score.recommendations:
            print(f"  ✅ {rec}")
    
    # Score Lifecycle
    lifecycle_score = scorer.score_lifecycle(zombie_count, decay_count, growth_count)
    print(f"\n{lifecycle_score.name}: {lifecycle_score.score}/10 {lifecycle_score.health.value}")
    if lifecycle_score.deficiencies:
        print(f"  ❌ Deficiencies: {', '.join(lifecycle_score.deficiencies)}")
    if lifecycle_score.recommendations:
        for rec in lifecycle_score.recommendations:
            print(f"  ✅ {rec}")
    
        # OVERALL SCORE WITH WEIGHTS
    from fx25.modules.module_scorer import ModuleScorer
    
    scorer_instance = ModuleScorer()
    scores_dict = {
        "shopify_client": shopify_score.score,
        "finance": finance_score.score,
        "lifecycle": lifecycle_score.score,
    }
    overall_score = scorer_instance.calculate_weighted_score(scores_dict)

    print_header(f"🏆 OVERALL SYSTEM SCORE: {overall_score:.1f}/10")
    
    if overall_score >= 8.5:
        print("🟢 READY TO SCALE - Sistema lista para crecer")
    elif overall_score >= 7.0:
        print("🟡 OPERATIONAL - Requiere optimizaciones")
    else:
        print("🔴 CRITICAL - Requiere atención inmediata")

if __name__ == "__main__":
    dashboard_intelligent()
