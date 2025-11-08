# fx25/modules/module_scorer.py - CON WEIGHTS
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict
from fx25.kv.sqlite_kv import get_kv_store

class ModuleHealth(Enum):
    CRITICAL = "🔴 CRÍTICO"
    WARNING = "🟡 ALERTA"
    HEALTHY = "🟢 SALUDABLE"
    OPTIMAL = "🟢🟢 ÓPTIMO"

@dataclass
class ModuleScore:
    name: str
    score: float
    health: ModuleHealth
    deficiencies: List[str]
    recommendations: List[str]

class ModuleScorer:
    # Weights optimizados por DeepSeek
    WEIGHTS = {
        "shopify_client": 0.4,    # Más crítico
        "finance": 0.3,           # Core del negocio
        "lifecycle": 0.2,         # Decisiones
        "alerts": 0.1             # Secondary
    }
    
    def __init__(self):
        self.kv = get_kv_store()
    
    def score_shopify_client(self, rate: float, breaker_state: str) -> ModuleScore:
        deficiencies = []
        recommendations = []
        score = 10.0
        
        if rate > 2.5:
            deficiencies.append("Rate limiter muy alto")
            recommendations.append("🔧 Reducir rate a 1.5 req/s")
            score -= 2.0
        elif rate < 0.5:
            deficiencies.append("Rate limiter muy bajo")
            recommendations.append("📈 Aumentar rate a 1.5 req/s")
            score -= 1.5
        
        if breaker_state == "OPEN":
            deficiencies.append("Circuit breaker abierto")
            recommendations.append("⚠️ Verificar errores de API")
            score -= 3.0
        
        health = self._get_health(score)
        return ModuleScore(
            name="ShopifyClient",
            score=round(score, 2),
            health=health,
            deficiencies=deficiencies,
            recommendations=recommendations
        )
    
    def score_finance(self, total_profit: float, total_revenue: float, avg_roas: float) -> ModuleScore:
        deficiencies = []
        recommendations = []
        score = 10.0
        
        if total_profit < 0:
            deficiencies.append("❌ Pérdida")
            recommendations.append("💰 Reducir costos")
            score -= 3.0
        elif total_profit < total_revenue * 0.1:
            deficiencies.append("⚠️ Margen bajo (<10%)")
            recommendations.append("📊 Aumentar precios")
            score -= 2.0
        
        if avg_roas < 1.0:
            deficiencies.append("ROAS < 1")
            recommendations.append("🚫 Pausar campañas")
            score -= 2.5
        elif avg_roas < 1.5:
            deficiencies.append("ROAS bajo (1-1.5)")
            recommendations.append("🎯 Mejorar targeting")
            score -= 1.0
        
        health = self._get_health(score)
        return ModuleScore(
            name="Finance",
            score=round(score, 2),
            health=health,
            deficiencies=deficiencies,
            recommendations=recommendations
        )
    
    def score_lifecycle(self, zombie_count: int, decay_count: int, growth_count: int) -> ModuleScore:
        deficiencies = []
        recommendations = []
        score = 10.0
        
        if zombie_count > 0:
            deficiencies.append(f"💀 {zombie_count} ZOMBIE")
            recommendations.append(f"🗑️ Descontinuar {zombie_count}")
            score -= zombie_count * 1.5
        
        if decay_count > 2:
            deficiencies.append(f"📉 {decay_count} DECAY")
            recommendations.append("🔄 Revitalizar")
            score -= decay_count * 0.5
        
        if growth_count == 0:
            deficiencies.append("📈 Sin GROWTH")
            recommendations.append("🚀 Nuevos productos")
            score -= 2.0
        
        health = self._get_health(score)
        return ModuleScore(
            name="Lifecycle",
            score=round(score, 2),
            health=health,
            deficiencies=deficiencies,
            recommendations=recommendations
        )
    
    def calculate_weighted_score(self, scores: Dict[str, float]) -> float:
        """Calcula score ponderado"""
        total = 0.0
        for module, score in scores.items():
            weight = self.WEIGHTS.get(module, 0.1)
            total += score * weight
        return round(total, 2)
    
    def _get_health(self, score: float) -> ModuleHealth:
        if score >= 9.0:
            return ModuleHealth.OPTIMAL
        elif score >= 7.0:
            return ModuleHealth.HEALTHY
        elif score >= 5.0:
            return ModuleHealth.WARNING
        else:
            return ModuleHealth.CRITICAL

def get_module_scorer() -> ModuleScorer:
    return ModuleScorer()
