# fx25/products/lifecycle.py
"""
Product Lifecycle: Detecta qué vender, qué optimizar, qué matar
- LAUNCH: Nuevo producto
- GROWTH: Ventas subiendo
- MATURE: Estable
- DECAY: Ventas bajando
- ZOMBIE: Muerto (vende casi nada)
"""

from enum import Enum
from fx25.kv.sqlite_kv import get_kv_store

class ProductState(Enum):
    LAUNCH = "LAUNCH"
    GROWTH = "GROWTH"
    MATURE = "MATURE"
    DECAY = "DECAY"
    ZOMBIE = "ZOMBIE"

class ProductLifecycle:
    def __init__(self):
        self.kv = get_kv_store()
    
    def track_sales(self, product_id: str, qty: int) -> None:
        """Registra venta"""
        key = f"sales:{product_id}"
        current = self.kv.get(key) or 0
        self.kv.set(key, current + qty)
    
    def get_state(self, product_id: str) -> ProductState:
        """Detecta estado del producto"""
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
    
    def recommend_action(self, product_id: str) -> str:
        """Recomendación de acción"""
        state = self.get_state(product_id)
        
        actions = {
            ProductState.LAUNCH: "🚀 PUSH - Invertir en marketing",
            ProductState.GROWTH: "📈 SCALE - Aumentar stock",
            ProductState.MATURE: "💰 OPTIMIZE - Mejorar márgenes",
            ProductState.DECAY: "⚠️ REVIEW - Analizar competencia",
            ProductState.ZOMBIE: "💀 KILL - Descontinuar",
        }
        
        return actions[state]

def get_lifecycle() -> ProductLifecycle:
    return ProductLifecycle()
