"""
=========================================================
sAI V1 - Database Manager
=========================================================
SQLite database manager for sAI.

Features
--------
- Automatic database creation
- Thread-safe operations
- Execute queries
- Fetch one / fetch all
- Insert / Update / Delete
=========================================================
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from threading import Lock

from config import DATA_DIR


class Database:

    def __init__(self, db_name: str = "sai.db"):

        self.db_path = Path(DATA_DIR) / db_name

        self.lock = Lock()

        self.connection = sqlite3.connect(
            self.db_path,
            check_same_thread=False,
        )

        self.connection.row_factory = sqlite3.Row

        self.cursor = self.connection.cursor()

    # -------------------------------------------------

    def execute(self, query: str, params=()):

        with self.lock:

            self.cursor.execute(query, params)

            self.connection.commit()

    # -------------------------------------------------

    def executemany(self, query: str, values):

        with self.lock:

            self.cursor.executemany(query, values)

            self.connection.commit()

    # -------------------------------------------------

    def fetchone(self, query: str, params=()):

        with self.lock:

            cur = self.connection.execute(query, params)

            row = cur.fetchone()

            if row is None:
                return None

            return dict(row)

    # -------------------------------------------------

    def fetchall(self, query: str, params=()):

        with self.lock:

            cur = self.connection.execute(query, params)

            rows = cur.fetchall()

            return [dict(r) for r in rows]

    # -------------------------------------------------

    def table_exists(self, table: str):

        row = self.fetchone(
            """
            SELECT name
            FROM sqlite_master
            WHERE type='table'
            AND name=?
            """,
            (table,),
        )

        return row is not None

    # -------------------------------------------------

    def create_tables(self):

        self.execute(
            """
            CREATE TABLE IF NOT EXISTS settings(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE,
                value TEXT
            )
            """
        )

        self.execute(
            """
            CREATE TABLE IF NOT EXISTS history(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT,
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        self.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task TEXT,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

    # -------------------------------------------------

    def insert_history(self, role: str, message: str):

        self.execute(
            """
            INSERT INTO history(role,message)
            VALUES(?,?)
            """,
            (role, message),
        )

    # -------------------------------------------------

    def history(self, limit: int = 50):

        return self.fetchall(
            """
            SELECT *
            FROM history
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        )

    # -------------------------------------------------

    def clear_history(self):

        self.execute(
            "DELETE FROM history"
        )

    # -------------------------------------------------

    def close(self):

        self.connection.close()


database = Database()

database.create_tables()


if __name__ == "__main__":

    print("Database Path:")

    print(database.db_path)

    print("Database Ready.")