import sqlite3
import json
from typing import Dict, Any

DB_PATH = "rental.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    d = dict(row)
    # Attempt to decode JSON fields
    for key, val in d.items():
        if isinstance(val, str) and (val.startswith('[') or val.startswith('{')):
            try:
                d[key] = json.loads(val)
            except Exception:
                pass
    return d

