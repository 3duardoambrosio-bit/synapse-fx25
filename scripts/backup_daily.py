# scripts/backup_daily.py
import shutil
import os
from datetime import datetime
from pathlib import Path

def backup_database():
    """Backup automático de la DB"""
    
    # Rutas
    db_path = Path("outputs/synapse_kv.db")
    backup_dir = Path("backups")
    
    # Crear carpeta si no existe
    backup_dir.mkdir(exist_ok=True)
    
    # Nombre con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"synapse_kv_{timestamp}.db"
    
    # Copiar DB
    if db_path.exists():
        shutil.copy2(db_path, backup_file)
        print(f"✅ Backup completado: {backup_file}")
    else:
        print(f"❌ DB no encontrada: {db_path}")
    
    # Eliminar backups > 7 días
    cleanup_old_backups(backup_dir)

def cleanup_old_backups(backup_dir: Path, days=7):
    """Elimina backups más antiguos que X días"""
    import time
    
    now = time.time()
    for backup_file in backup_dir.glob("*.db"):
        file_age_days = (now - backup_file.stat().st_mtime) / 86400
        if file_age_days > days:
            backup_file.unlink()
            print(f"🗑️ Eliminado backup antiguo: {backup_file.name}")

if __name__ == "__main__":
    backup_database()
