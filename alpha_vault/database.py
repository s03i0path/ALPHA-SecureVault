import os
import sqlite3
from pathlib import Path
from typing import Optional

DEFAULT_DIR = Path.home() / ".alpha_secure_vault"
DEFAULT_DB = DEFAULT_DIR / "vault.db"

class VaultDatabase:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = str(db_path or DEFAULT_DB)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize(self):
        with self.connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password_salt BLOB NOT NULL,
                    password_hash BLOB NOT NULL,
                    vault_salt BLOB NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    encrypted_payload BLOB NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)

    def create_user(self, username, password_salt, password_digest, vault_salt):
        with self.connect() as conn:
            cur = conn.execute(
                "INSERT INTO users(username, password_salt, password_hash, vault_salt) VALUES (?, ?, ?, ?)",
                (username, password_salt, password_digest, vault_salt)
            )
            return cur.lastrowid

    def get_user(self, username):
        with self.connect() as conn:
            return conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

    def add_entry(self, user_id, encrypted_payload):
        with self.connect() as conn:
            cur = conn.execute(
                "INSERT INTO entries(user_id, encrypted_payload) VALUES (?, ?)",
                (user_id, encrypted_payload)
            )
            return cur.lastrowid

    def list_entries(self, user_id):
        with self.connect() as conn:
            return conn.execute(
                "SELECT id, encrypted_payload FROM entries WHERE user_id = ? ORDER BY id DESC",
                (user_id,)
            ).fetchall()

    def update_entry(self, entry_id, user_id, encrypted_payload):
        with self.connect() as conn:
            cur = conn.execute(
                "UPDATE entries SET encrypted_payload = ? WHERE id = ? AND user_id = ?",
                (encrypted_payload, entry_id, user_id)
            )
            return cur.rowcount == 1

    def delete_entry(self, entry_id, user_id):
        with self.connect() as conn:
            cur = conn.execute(
                "DELETE FROM entries WHERE id = ? AND user_id = ?",
                (entry_id, user_id)
            )
            return cur.rowcount == 1
