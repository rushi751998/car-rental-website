#!/usr/bin/env python3
"""
Database Migration Script
Adds full_name column to users table and updates sessions/chat_logs tables
"""
import sqlite3
import sys


def migrate_database(db_path="rental.db"):
    """Run database migrations"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print("Starting database migration...")

        # Step 1: Recreate users table to remove username NOT NULL constraint
        print("Migrating users table structure...")

        # Check current table structure
        cursor.execute("PRAGMA table_info(users)")
        users_columns = [col[1] for col in cursor.fetchall()]

        if "username" in users_columns:
            # Create new users table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    full_name TEXT,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """
            )

            # Copy existing data (username will be dropped, full_name will be NULL for old records)
            cursor.execute(
                """
                INSERT INTO users_new (id, full_name, email, password_hash, created_at)
                SELECT id, NULL, email, password_hash, created_at FROM users
            """
            )

            cursor.execute("DROP TABLE users")
            cursor.execute("ALTER TABLE users_new RENAME TO users")
            print("✅ Migrated users table (removed username, added full_name)")
        elif "full_name" not in users_columns:
            cursor.execute("ALTER TABLE users ADD COLUMN full_name TEXT")
            print("✅ Added full_name column to users table")
        else:
            print("⚠️  users table already has correct structure")

        # Step 2: Check if sessions table needs migration
        cursor.execute("PRAGMA table_info(sessions)")
        sessions_columns = [col[1] for col in cursor.fetchall()]

        if "user_id" in sessions_columns and "user_email" not in sessions_columns:
            print("Migrating sessions table from user_id to user_email...")

            # Create new sessions table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_email TEXT,
                    token TEXT UNIQUE NOT NULL,
                    created_at TEXT NOT NULL
                )
            """
            )

            # Copy data (this won't work perfectly without user data, so we'll clear old sessions)
            cursor.execute("DROP TABLE IF EXISTS sessions")
            cursor.execute("ALTER TABLE sessions_new RENAME TO sessions")
            print("✅ Migrated sessions table to use user_email")
        else:
            print("⚠️  sessions table already uses user_email or doesn't exist")

        # Step 3: Check if chat_logs table needs migration
        cursor.execute("PRAGMA table_info(chat_logs)")
        chat_columns = [col[1] for col in cursor.fetchall()]

        if "user_id" in chat_columns and "user_email" not in chat_columns:
            print("Migrating chat_logs table from user_id to user_email...")

            # Create new chat_logs table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS chat_logs_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    user_email TEXT,
                    role TEXT NOT NULL,
                    message TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """
            )

            # Copy existing data
            cursor.execute(
                """
                INSERT INTO chat_logs_new (session_id, user_email, role, message, created_at)
                SELECT session_id, NULL, role, message, created_at FROM chat_logs
            """
            )

            cursor.execute("DROP TABLE chat_logs")
            cursor.execute("ALTER TABLE chat_logs_new RENAME TO chat_logs")
            print("✅ Migrated chat_logs table to use user_email")
        else:
            print("⚠️  chat_logs table already uses user_email or doesn't exist")

        # Commit changes
        conn.commit()
        print("\n✅ Database migration completed successfully!")
        print("\nNext steps:")
        print("1. Restart your server: python main.py")
        print("2. Test registration at: http://localhost:5000/register.html")
        print("3. Test login at: http://localhost:5000/login.html")

        conn.close()
        return True

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False


if __name__ == "__main__":
    db_file = sys.argv[1] if len(sys.argv) > 1 else "rental.db"
    success = migrate_database(db_file)
    sys.exit(0 if success else 1)
