"""
=========================================================
sAI V1 - Personal Profile Memory
=========================================================
Stores personal facts separately from chat history.
=========================================================
"""

from __future__ import annotations

import json
from pathlib import Path


class ProfileMemory:

    def __init__(self, filename="data/profile.json"):

        self.path = Path(filename)

        self.path.parent.mkdir(parents=True, exist_ok=True)

        if not self.path.exists():
            self.path.write_text("{}")

        self.load()

    # ----------------------------------------------

    def load(self):

        try:

            self.data = json.loads(
                self.path.read_text(encoding="utf-8")
            )

        except Exception:

            self.data = {}

    # ----------------------------------------------

    def save(self):

        self.path.write_text(
            json.dumps(
                self.data,
                indent=4,
            ),
            encoding="utf-8",
        )

    # ----------------------------------------------

    def remember(self, key, value):

        self.data[key.lower()] = value

        self.save()

    # ----------------------------------------------

    def recall(self, key):

        return self.data.get(key.lower())

    # ----------------------------------------------

    def all(self):

        return self.data

    # ----------------------------------------------

    def clear(self):

        self.data = {}

        self.save()