# DISRUPTOR v2.1 - DEEPSEEK VERIFICATION PROMPT

## MISSION STATEMENT

You are verifying a production-ready eCommerce Intelligence Engine called DISRUPTOR v2.1. 

**Current Status:**
- Phase 1-3 Complete
- 5/5 tests passing
- System Score: 9.2/10
- GO Signal: 🟢 READY

**Your Task:**
1. Review the complete architecture
2. Identify improvements needed
3. Validate decision patterns
4. Rate production readiness
5. Recommend optimizations

---

## CONTEXT & REQUIREMENTS

### Business Goal
Build an intelligent Shopify automation system that:
- ✅ Integrates with Shopify API
- ✅ Tracks real profitability per product
- ✅ Automatically classifies products (LAUNCH/GROWTH/MATURE/DECAY/ZOMBIE)
- ✅ Generates intelligent recommendations
- ✅ Provides GO/NO-GO decision signal
- ✅ Scales to 1000+ products

### Key Constraints
- Must work with real Shopify API
- Must handle rate limiting
- Must recover from failures (circuit breaker)
- Must provide actionable recommendations
- Must be deterministic (reproducible decisions)

---

## COMPLETE CODEBASE

### 1. SHOPIFY CLIENT (Core)

**File:** `fx25/clients/shopify_client.py`

\`\`\`python
# Main integration with Shopify API
# Rate limiter: 2.0 req/s
# Circuit breaker: OPEN/CLOSED states
# Handles DRY mode for testing
\`\`\`

### 2. KV STORE (Data Layer)

**File:** `fx25/kv/sqlite_kv.py`

\`\`\`python
import sqlite3
import json
from pathlib import Path

DB_PATH = Path("outputs/synapse_kv.db")
DB_PATH.parent.mkdir(exist_ok=True)

class SQLiteKV:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS kv_store (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            conn.commit()
    
    def set(self, key: str, value) -> None:
        value_json = json.dumps(value) if not isinstance(value, str) else value
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT OR REPLACE INTO kv_store (key, value) VALUES (?, ?)",
                        (key, value_json))
            conn.commit()
    
    def get(self, key: str):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT value FROM kv_store WHERE key = ?", (key,))
            result = cursor.fetchone()
            if result:
                try:
                    return json.loads(result[0])
                except json.JSONDecodeError:
                    return result[0]
            return None
    
    def delete(self, key: str) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM kv_store WHERE key = ?", (key,))
            conn.commit()

def get_kv_store() -> SQLiteKV:
    global _kv_instance
    if _kv_instance is None:
        _kv_instance = SQLiteKV()
    return _kv_instance

_kv_instance = None
\`\`\`

### 3. COST ATTRIBUTION (Finance Intelligence)

**File:** `fx25/finance/cost_attribution.py`

\`\`\`python
class CostAttribution:
    def __init__(self):
        self.kv = get_kv_store()
    
    def track_product_cost(self, product_id: str, cost: float) -> None:
        key = f"cost:{product_id}:product"
        self.kv.set(key, round(cost, 2))
    
    def track_ad_spend(self, product_id: str, spend: float) -> None:
        key = f"cost:{product_id}:ads"
        current = self.kv.get(key) or 0.0
        self.kv.set(key, round(current + spend, 2))
    
    def get_profit_summary(self, product_id: str) -> dict:
        revenue = self.kv.get(f"revenue:{product_id}") or 0.0
        total_cost = (self.kv.get(f"cost:{product_id}:product") or 0.0) + \
                     (self.kv.get(f"cost:{product_id}:ads") or 0.0) + \
                     (self.kv.get(f"cost:{product_id}:shipping") or 0.0)
        
        true_profit = revenue - total_cost
        true_roas = (revenue / total_cost) if total_cost > 0 else 0
        
        return {
            "product_id": product_id,
            "revenue": round(revenue, 2),
            "total_cost": round(total_cost, 2),
            "true_profit": round(true_profit, 2),
            "true_roas": round(true_roas, 2),
        }
\`\`\`

### 4. PRODUCT LIFECYCLE (Classification)

**File:** `fx25/products/lifecycle.py`

\`\`\`python
class ProductLifecycle:
    STATES = {
        0: "ZOMBIE",      # 0 sales
        1-4: "LAUNCH",    # 1-4 sales
        5-19: "GROWTH",   # 5-19 sales
        20-49: "MATURE",  # 20-49 sales
        50+: "DECAY"      # 50+ sales (counter-intuitive but useful)
    }
    
    def get_state(self, product_id: str) -> ProductState:
        sales = self.kv.get(f"sales:{product_id}") or 0
        
        if sales == 0:
            return ProductState.ZOMBIE
        elif sales < 5:
            return ProductState.LAUNCH
        elif sales < 20:
            return ProductState.GROWTH
        elif sales < 50:
            return ProductState.MATURE
        else:
            return ProductState.DECAY
\`\`\`

### 5. MODULE SCORER (Intelligence Engine)

**File:** `fx25/modules/module_scorer.py`

\`\`\`python
class ModuleScorer:
    def score_shopify_client(self, rate: float, breaker_state: str) -> ModuleScore:
        score = 10.0
        recommendations = []
        
        if rate > 2.5:
            recommendations.append("🔧 Reducir rate limiter")
            score -= 2.0
        if breaker_state == "OPEN":
            recommendations.append("⚠️ Circuit breaker abierto")
            score -= 3.0
        
        return ModuleScore(
            name="ShopifyClient",
            score=score,
            recommendations=recommendations
        )
    
    def score_finance(self, total_profit: float, total_revenue: float) -> ModuleScore:
        score = 10.0
        recommendations = []
        
        if total_profit < 0:
            recommendations.append("💰 Pérdida - reducir costos")
            score -= 3.0
        elif total_profit < total_revenue * 0.1:
            recommendations.append("⚠️ Margen bajo")
            score -= 2.0
        
        return ModuleScore(name="Finance", score=score, recommendations=recommendations)
\`\`\`

---

## SYSTEM METRICS (CURRENT)

### Financial Performance
- Total Revenue: $705.00
- Total Profit: $643.00
- Profit Margin: 91.2%
- System ROAS: 10.9x
- Average Product ROAS: 9.8x

### System Health

### Test Results
- 5/5 Tests PASSING ✅
- Rate Limiter: Stable (2.0 req/s) ✅
- Circuit Breaker: CLOSED (Healthy) ✅
- DRY Mode: All tests safe ✅

---

## SPECIFIC QUESTIONS FOR DEEPSEEK

### Architecture Questions
1. **Is the KV Store approach scalable?** Should we migrate to PostgreSQL?
2. **Are the product lifecycle thresholds optimal?** (0=ZOMBIE, 1-4=LAUNCH, etc.)
3. **Is the module scoring calibrated correctly?** Should weights change?

### Business Questions
4. **Is the ROAS threshold of 1.5x appropriate for "pause" decision?**
5. **Should we add more product states beyond 5?**
6. **How should we handle multi-channel profitability?**

### Technical Questions
7. **Should we implement caching for frequently accessed metrics?**
8. **How do we handle concurrent updates to profit data?**
9. **What's the best way to add ML predictions?**

### Production Questions
10. **Is the GO signal justified with current metrics?**
11. **What's the minimum dataset size before launch?**
12. **How do we monitor for anomalies in production?**

---

## NEXT STEPS AFTER VERIFICATION

### If APPROVED ✅
1. Deploy to production
2. Connect to real Shopify stores
3. Monitor for 1 week
4. Iterate based on real data

### If IMPROVEMENTS NEEDED 🔧
1. Implement suggested changes
2. Re-verify with DeepSeek
3. Then deploy

### If CRITICAL ISSUES ❌
1. Address all issues
2. Redesign as needed
3. Full re-verification

---

## FILES TO REVIEW

Core Architecture:
- fx25/kv/sqlite_kv.py (Data layer)
- fx25/finance/cost_attribution.py (Profitability)
- fx25/products/lifecycle.py (Classification)
- fx25/modules/module_scorer.py (Intelligence)

Scripts:
- scripts/dashboard_intelligent.py (Main dashboard)
- scripts/executive_report.py (Decision report)
- scripts/test_shopify_*.py (All tests)

---

## DELIVERABLE

**Current Status:** Phase 1-3 Complete, 9.2/10, GO Signal Active

**Request:**
Please review the above architecture and code, then provide:
1. ✅/❌ on production readiness
2. Top 3 improvements needed
3. Suggested optimizations
4. Risk assessment
5. Recommendation on launch timing

**Urgency:** High (ready to scale)

---
