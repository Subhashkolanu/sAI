"""
=========================================================
sAI V1 - Memory System
=========================================================
Persistent conversation memory using SQLite.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

from config import MEMORY_DB


class Memory:
    def __init__(self, db_path: Path | str = MEMORY_DB):
        self.db_path = str(db_path)
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.cursor = self.connection.cursor()
        self._create_tables()

    # --------------------------------------------------

    def _create_tables(self):
        self.cursor.execute(
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

    # --------------------------------------------------

    def add(self, role: str, message: str):

        self.cursor.execute(
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

    # --------------------------------------------------

    def recent(self, limit: int = 20):

        rows = self.cursor.execute(
            """
            SELECT role, message, timestamp
            FROM conversations
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

        return [dict(row) for row in reversed(rows)]

    # --------------------------------------------------

    def all(self):

        rows = self.cursor.execute(
            """
            SELECT role, message, timestamp
            FROM conversations
            ORDER BY id
            """
        ).fetchall()

        return [dict(row) for row in rows]

    # --------------------------------------------------

    def search(self, keyword: str):

        rows = self.cursor.execute(
            """
            SELECT role, message, timestamp
            FROM conversations
            WHERE message LIKE ?
            ORDER BY id
            """,
            (f"%{keyword}%",),
        ).fetchall()

        return [dict(row) for row in rows]

    # --------------------------------------------------

    def count(self):

        return self.cursor.execute(
            "SELECT COUNT(*) FROM conversations"
        ).fetchone()[0]

    # --------------------------------------------------

    def clear(self):

        self.cursor.execute("DELETE FROM conversations")
        self.connection.commit()

    # --------------------------------------------------

    def delete(self, record_id: int):

        self.cursor.execute(
            "DELETE FROM conversations WHERE id=?",
            (record_id,),
        )

        self.connection.commit()

    # --------------------------------------------------

    def close(self):

        self.connection.close()

    # --------------------------------------------------

    def __del__(self):

        try:
            self.connection.close()
        except Exception:
            pass