from typing import Any, Dict, List, Optional, Sequence
import sqlite3

from src.db import DB_PATH, row_to_dict

class Database:
    """
    Simple OOP wrapper around SQLite operations.
    All methods accept a SQL query string and parameters, and open/close
    a connection per call to keep things thread-safe with FastAPI.
    """
    def __init__(self, db_path: str = DB_PATH) -> None:
        self.db_path = db_path

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    # Read operations
    def fetchall(self, sql: str, params: Sequence[Any] = ()) -> List[sqlite3.Row]:
        conn = self._connect()
        cur = conn.cursor()
        cur.execute(sql, params)
        rows = cur.fetchall()
        conn.close()
        return rows

    def fetchall_dicts(self, sql: str, params: Sequence[Any] = ()) -> List[Dict[str, Any]]:
        return [row_to_dict(r) for r in self.fetchall(sql, params)]

    def fetchone(self, sql: str, params: Sequence[Any] = ()) -> Optional[sqlite3.Row]:
        conn = self._connect()
        cur = conn.cursor()
        cur.execute(sql, params)
        row = cur.fetchone()
        conn.close()
        return row

    def fetchone_dict(self, sql: str, params: Sequence[Any] = ()) -> Optional[Dict[str, Any]]:
        r = self.fetchone(sql, params)
        return row_to_dict(r) if r else None

    # Write operations
    def execute(self, sql: str, params: Sequence[Any] = ()) -> int:
        conn = self._connect()
        cur = conn.cursor()
        cur.execute(sql, params)
        conn.commit()
        # sqlite3 cursor.rowcount may be -1 depending on driver; use changes()
        try:
            count = cur.rowcount
            if count == -1:
                count = cur.execute("SELECT changes()").fetchone()[0]
        except Exception:
            count = 0
        conn.close()
        return count

    def insert(self, sql: str, params: Sequence[Any] = ()) -> int:
        conn = self._connect()
        cur = conn.cursor()
        cur.execute(sql, params)
        conn.commit()
        last_id = cur.lastrowid
        conn.close()
        return last_id

    # Convenience methods
    def verify_admin(self, username: str, password: str) -> bool:
        row = self.fetchone(
            "SELECT * FROM admin WHERE username = ? AND password = ?",
            (username, password),
        )
        return row is not None

# Module-level convenience instance
db = Database()

# Initialize database
def init_db():
    # Cars table
    db.execute('''
        CREATE TABLE IF NOT EXISTS cars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            model TEXT NOT NULL,
            price_per_day REAL NOT NULL,
            seats INTEGER NOT NULL,
            transmission TEXT NOT NULL,
            fuel_type TEXT NOT NULL,
            images TEXT NOT NULL,
            description TEXT,
            available BOOLEAN DEFAULT 1
        )
    ''')

    # Picnic spots table
    db.execute('''
        CREATE TABLE IF NOT EXISTS picnic_spots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            location TEXT NOT NULL,
            images TEXT NOT NULL,
            short_description TEXT,
            detailed_description TEXT,
            available BOOLEAN DEFAULT 1
        )
    ''')

    # Add new JSON columns if the table already exists
    try:
        db.execute("ALTER TABLE picnic_spots ADD COLUMN trip_images TEXT")
    except Exception:
        pass
    try:
        db.execute("ALTER TABLE picnic_spots ADD COLUMN hotel_images TEXT")
    except Exception:
        pass

    # Admin table
    db.execute('''
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # PI: UserAuth - Users and Sessions tables
    db.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    db.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')

    # PI: Chatbot - Chat logs table
    db.execute('''
        CREATE TABLE IF NOT EXISTS chat_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            user_id INTEGER,
            role TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE SET NULL
        )
    ''')

    # PI: LastTrips - tables for last trips and comments
    db.execute('''
        CREATE TABLE IF NOT EXISTS last_trips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            destination TEXT NOT NULL,
            spots TEXT NOT NULL,
            days INTEGER NOT NULL,
            persons INTEGER NOT NULL,
            images TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            feedback TEXT,
            created_at TEXT NOT NULL,
            available BOOLEAN DEFAULT 1
        )
    ''')
    db.execute('''
        CREATE TABLE IF NOT EXISTS last_trip_comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trip_id INTEGER NOT NULL,
            name TEXT,
            comment TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(trip_id) REFERENCES last_trips(id) ON DELETE CASCADE
        )
    ''')

    # Insert default admin if not exists
    if not db.fetchone("SELECT 1 FROM admin WHERE username = ?", ('admin',)):
        db.execute("INSERT INTO admin (username, password) VALUES (?, ?)", ('admin', 'admin123'))

init_db()

def verify_admin(username: str, password: str) -> bool:
    return db.verify_admin(username, password)
