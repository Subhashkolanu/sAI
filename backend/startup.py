"""
=========================================================
sAI V1 - Startup Manager
=========================================================
Performs startup checks before launching sAI.
=========================================================
"""

from __future__ import annotations

import os
import platform
import shutil
import socket
import sys
from pathlib import Path

from config import (
    ASSISTANT_NAME,
    VERSION,
    DATA_DIR,
    CACHE_DIR,
    MEMORY_DIR,
    LOG_DIR,
    TEMP_DIR,
    UPLOAD_DIR,
)


class StartupManager:

    def __init__(self):

        self.results = []

    # -------------------------------------------------

    def check_python(self):

        version = sys.version.split()[0]

        self.results.append(
            ("Python", version, True)
        )

    # -------------------------------------------------

    def check_platform(self):

        self.results.append(
            (
                "Platform",
                platform.system(),
                True,
            )
        )

    # -------------------------------------------------

    def check_directories(self):

        folders = [
            DATA_DIR,
            CACHE_DIR,
            MEMORY_DIR,
            LOG_DIR,
            TEMP_DIR,
            UPLOAD_DIR,
        ]

        for folder in folders:

            folder.mkdir(
                parents=True,
                exist_ok=True,
            )

            self.results.append(
                (
                    folder.name,
                    "OK",
                    True,
                )
            )

    # -------------------------------------------------

    def check_ollama(self):

        found = shutil.which("ollama") is not None

        self.results.append(
            (
                "Ollama",
                "Installed" if found else "Not Found",
                found,
            )
        )

    # -------------------------------------------------

    def check_openai(self):

        key = os.getenv("OPENAI_API_KEY", "")

        self.results.append(
            (
                "OpenAI Key",
                "Configured" if key else "Not Configured",
                bool(key),
            )
        )

    # -------------------------------------------------

    def check_network(self):

        try:

            socket.create_connection(
                ("8.8.8.8", 53),
                timeout=2,
            )

            status = True

        except Exception:

            status = False

        self.results.append(
            (
                "Internet",
                "Connected" if status else "Offline",
                status,
            )
        )

    # -------------------------------------------------

    def run(self):

        self.results.clear()

        self.check_python()

        self.check_platform()

        self.check_directories()

        self.check_ollama()

        self.check_openai()

        self.check_network()

        return self.results

    # -------------------------------------------------

    def report(self):

        print("\n")

        print("=" * 60)

        print(f"{ASSISTANT_NAME} v{VERSION} Startup Report")

        print("=" * 60)

        for name, value, ok in self.results:

            icon = "✓" if ok else "✗"

            print(f"{icon} {name:<18} {value}")

        print("=" * 60)


if __name__ == "__main__":

    startup = StartupManager()

    startup.run()

    startup.report()