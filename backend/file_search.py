"""
=========================================================
sAI V1 - Smart File Search
=========================================================
Searches files on the local computer.
=========================================================
"""

from __future__ import annotations

from pathlib import Path


class FileSearch:

    def __init__(self):

        self.search_locations = [
            Path.home() / "Desktop",
            Path.home() / "Documents",
            Path.home() / "Downloads",
        ]

    # --------------------------------------------------

    def search(self, keyword: str, limit: int = 20):

        keyword = keyword.lower().strip()

        results = []

        for folder in self.search_locations:

            if not folder.exists():
                continue

            try:

                for file in folder.rglob("*"):

                    if keyword in file.name.lower():

                        results.append(str(file))

                        if len(results) >= limit:
                            return results

            except Exception:
                continue

        return results

    # --------------------------------------------------

    def add_location(self, folder):

        folder = Path(folder)

        if folder.exists() and folder not in self.search_locations:
            self.search_locations.append(folder)