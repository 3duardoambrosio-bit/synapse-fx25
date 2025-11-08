# fx25/kv/sqlite_kv.py - CON CACHE
import sqlite3
import json
import time
from pathlib import Path

DB_PATH = Path("outputs/synapse_kv.db")
DB_PATH.parent.mkdir(exist_ok=True)

class CachedSQLiteKV:
    def __init__(self, db_path=DB_PATH, cache_ttl=300):
        self.db_path = db_path
        self.cache_ttl = cache_ttl
        self._cache = {}
        self._cache_times = {}
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
        """Store with cache update"""
        value_json = json.dumps(value) if not isinstance(value, str) else value
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT OR REPLACE INTO kv_store (key, value) VALUES (?, ?)",
                        (key, value_json))
            conn.commit()
        # Update cache
        self._cache[key] = value
        self._cache_times[key] = time.time()
    
    def get(self, key: str):
        """Get with cache - returns from memory if fresh"""
        now = time.time()
        
        # Check cache
        if key in self._cache:
            cache_age = now - self._cache_times.get(key, 0)
            if cache_age < self.cache_ttl:
                return self._cache[key]
        
        # Cache miss - read from DB
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT value FROM kv_store WHERE key = ?", (key,))
            result = cursor.fetchone()
            if result:
                try:
                    value = json.loads(result[0])
                except json.JSONDecodeError:
                    value = result[0]
                # Store in cache
                self._cache[key] = value
                self._cache_times[key] = now
                return value
        return None
    
    def delete(self, key: str) -> None:
        """Delete from DB and cache"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM kv_store WHERE key = ?", (key,))
            conn.commit()
        if key in self._cache:
            del self._cache[key]
            del self._cache_times[key]

_kv_instance = None

def get_kv_store() -> CachedSQLiteKV:
    global _kv_instance
    if _kv_instance is None:
        _kv_instance = CachedSQLiteKV()
    return _kv_instance
