"""
=========================================================
sAI V1 - Core Assistant
=========================================================
AI + Desktop Control + Personal Memory
=========================================================
"""

from __future__ import annotations

import re
from datetime import datetime

from backend.desktop import DesktopController
from backend.llm import LLM
from backend.memory import Memory
from backend.profile_memory import ProfileMemory


class Assistant:

    def __init__(self):

        self.llm = LLM()
        self.memory = Memory()
        self.profile = ProfileMemory()

        self.chat_history = []

    # --------------------------------------------------

    def timestamp(self):
        return datetime.now().strftime("%H:%M:%S")

    # --------------------------------------------------

    def add_history(self, role, message):

        self.chat_history.append(
            {
                "role": role,
                "message": message,
                "time": self.timestamp(),
            }
        )

    # --------------------------------------------------

    def history(self):
        return self.chat_history

    # --------------------------------------------------

    def clear_history(self):
        self.chat_history.clear()

    # --------------------------------------------------
    # PERSONAL MEMORY
    # --------------------------------------------------

    def personal_memory(self, prompt):

        text = prompt.lower().strip()

        patterns = [
            ("my name is", "name"),
            ("my favourite language is", "favourite_language"),
            ("my favorite language is", "favourite_language"),
            ("my college is", "college"),
            ("my city is", "city"),
        ]

        for phrase, key in patterns:

            if phrase in text:

                value = prompt.split(phrase, 1)[1].strip()

                self.profile.remember(key, value)

                return f"I'll remember that. Your {key.replace('_',' ')} is {value}."

        questions = {
            "what is my name": "name",
            "what's my name": "name",
            "what is my favourite language": "favourite_language",
            "what's my favourite language": "favourite_language",
            "what is my college": "college",
            "what's my college": "college",
            "what is my city": "city",
            "what's my city": "city",
        }

        for q, key in questions.items():

            if text == q:

                value = self.profile.recall(key)

                if value:

                    return f"Your {key.replace('_',' ')} is {value}."

                return f"I don't know your {key.replace('_',' ')} yet."

        return None

    # --------------------------------------------------
    # DESKTOP COMMANDS
    # --------------------------------------------------

    def desktop_commands(self, prompt):

        text = prompt.lower()

        apps = [
            "chrome",
            "edge",
            "vscode",
            "notepad",
            "calculator",
            "paint",
            "explorer",
        ]

        for app in apps:

            if f"open {app}" in text:

                if DesktopController.open_app(app):

                    return f"Opening {app.title()}..."

                return f"{app.title()} not found."

        folders = [
            "desktop",
            "downloads",
            "documents",
            "pictures",
            "videos",
            "music",
        ]

        for folder in folders:

            if f"open {folder}" in text:

                DesktopController.open_folder(folder)

                return f"Opening {folder.title()}..."

        websites = {
            "github": "https://github.com",
            "youtube": "https://youtube.com",
            "google": "https://google.com",
        }

        for site, url in websites.items():

            if f"open {site}" in text:

                DesktopController.open_website(url)

                return f"Opening {site.title()}..."

        return None

    # --------------------------------------------------

    def reply(self, prompt):

        prompt = prompt.strip()

        if not prompt:
            return "Please enter a message."

        self.memory.add("user", prompt)

        self.add_history("user", prompt)

        result = self.personal_memory(prompt)

        if result:

            self.memory.add("assistant", result)

            self.add_history("assistant", result)

            return result

        result = self.desktop_commands(prompt)

        if result:

            self.memory.add("assistant", result)

            self.add_history("assistant", result)

            return result

        try:

            response = self.llm.generate(prompt)

        except Exception as e:

            response = str(e)

        self.memory.add("assistant", response)

        self.add_history("assistant", response)

        return response