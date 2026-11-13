"""Tiny SQLite user store. Only account data is stored - never residents' queries."""
import sqlite3
from contextlib import contextmanager

from backend.config import settings


def init_db() -> None:
    settings.db_path.parent.mkdir(parents=True, exist_ok=True)
    with connect() as conn:
        conn.execute(
            """CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT DEFAULT '',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )"""
        )


@contextmanager
def connect():
    conn = sqlite3.connect(settings.db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def get_user(username: str):
    with connect() as conn:
        return conn.execute(
            "SELECT * FROM users WHERE username = ?", (username.lower(),)
        ).fetchone()


def create_user(username: str, password_hash: str, full_name: str = "") -> None:
    with connect() as conn:
        conn.execute(
            "INSERT INTO users (username, password_hash, full_name) VALUES (?, ?, ?)",
            (username.lower(), password_hash, full_name),
        )


def set_password(username: str, password_hash: str) -> None:
    with connect() as conn:
        conn.execute(
            "UPDATE users SET password_hash = ? WHERE username = ?",
            (password_hash, username.lower()),
        )
