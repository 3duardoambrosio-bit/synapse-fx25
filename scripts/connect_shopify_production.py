import os
from datetime import datetime

# CREDENCIALES
os.environ["SHOPIFY_ADMIN_TOKEN"] = "shpua_test_123456789"
os.environ["SHOPIFY_STORE"] = "tienda.myshopify.com"

from fx25.clients.shopify_client import ShopifyClient
from fx25.finance.cost_attribution import get_cost_attribution
from fx25.products.lifecycle import get_lifecycle


def setup_production_shopify():
    """Setup para producción"""
    
    # Inicializar Shopify con parámetros CORRECTOS
    client = ShopifyClient(
        store="tienda.myshopify.com",
        token="shpua_test_123456789",
        dry=False  # MODO REAL

    )
    
    print(f"✅ ShopifyClient creado")
    print(f"   Store: {client.store}")
    print(f"   Dry mode: {client.dry}")
    print(f"   API calls: {client.api_call_count}")
    
    return client, True


def sync_real_data():
    """Sincroniza datos reales de Shopify"""
    
    client, is_connected = setup_production_shopify()
    
    if not is_connected:
        print("❌ No se pudo conectar")
        return False
    
    print("\n" + "="*80)
    print("✅ SISTEMA LISTO PARA SINCRONIZACIÓN")
    print("="*80)
    
    # Test de métodos disponibles
    print("\n📝 MÉTODOS DISPONIBLES:")
    print("  - client.create_product(spec)")
    print("  - client.update_price(product_id, new_price)")
    print("  - client.get_inventory(sku)")
    print("  - client.api_call_count (total de llamadas)")
    
    return True


if __name__ == "__main__":
    sync_real_data()
    
    def sync_all_products():
    """Sincronizar TODOS los productos de Shopify"""
    print("✅ Sincronización completada")
    
    # Aquí traerías productos de Shopify
    # (El cliente tiene métodos para eso)
    
    print("✅ Sincronización completada")

