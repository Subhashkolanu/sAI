"""
=========================================================
sAI V1 - Memory System
=========================================================
Persistent conversation memory using SQLite.
=========================================================
"""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from threading import RLock

from backend.config import MEMORY_DB


_DATABASE_LOCKS: dict[str, RLock] = {}


class Memory:
    def __init__(self, db_path: Path | str = MEMORY_DB):
        self.db_path = str(Path(db_path).resolve())
        self.lock = _DATABASE_LOCKS.setdefault(self.db_path, RLock())
        self.closed = False
        self.connection = sqlite3.connect(
            self.db_path,
            check_same_thread=False,
            timeout=5.0,
        )
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA busy_timeout = 5000")
        self.connection.execute("PRAGMA journal_mode = WAL")
        self._create_tables()

    def _create_tables(self):
        with self.lock:
            self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS conversations(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    message TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
                """
            )
            self.connection.commit()

    def add(self, role: str, message: str):
        with self.lock:
            self.connection.execute(
                """
                INSERT INTO conversations(role, message, timestamp)
                VALUES (?, ?, ?)
                """,
                (
                    role,
                    message,
                    datetime.now().isoformat(timespec="seconds"),
                ),
            )
            self.connection.commit()

    def recent(self, limit: int = 20):
        with self.lock:
            rows = self.connection.execute(
                """
                SELECT role, message, timestamp
                FROM conversations
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [dict(row) for row in reversed(rows)]

    def all(self):
        with self.lock:
            rows = self.connection.execute(
                """
                SELECT role, message, timestamp
                FROM conversations
                ORDER BY id
                """
            ).fetchall()

        return [dict(row) for row in rows]

    def search(self, keyword: str):
        with self.lock:
            rows = self.connection.execute(
                """
                SELECT role, message, timestamp
                FROM conversations
                WHERE message LIKE ?
                ORDER BY id
                """,
                (f"%{keyword}%",),
            ).fetchall()

        return [dict(row) for row in rows]

    def count(self):
        with self.lock:
            return self.connection.execute(
                "SELECT COUNT(*) FROM conversations"
            ).fetchone()[0]

    def clear(self):
        with self.lock:
            self.connection.execute("DELETE FROM conversations")
            self.connection.commit()

    def delete(self, record_id: int):
        with self.lock:
            self.connection.execute(
                "DELETE FROM conversations WHERE id=?",
                (record_id,),
            )
            self.connection.commit()

    def close(self):
        with self.lock:
            if not self.closed:
                self.connection.close()
                self.closed = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        self.close()

    def __del__(self):
        try:
            self.connection.close()
        except Exception:
            pass
