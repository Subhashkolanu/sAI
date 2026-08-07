"""
=========================================================
sAI V1 - Core Assistant
=========================================================
AI + Desktop + Personal Memory + File Search
=========================================================
"""

from __future__ import annotations

from datetime import datetime

from backend.desktop import DesktopController
from backend.file_search import FileSearch
from backend.llm import LLM
from backend.memory import Memory
from backend.profile_memory import ProfileMemory


class Assistant:

    def __init__(self):

        self.llm = LLM()
        self.memory = Memory()
        self.profile = ProfileMemory()
        self.search = FileSearch()

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

        memory_patterns = {
            "my name is": "name",
            "my favourite language is": "favourite_language",
            "my favorite language is": "favourite_language",
            "my favourite coding language is": "favourite_language",
            "my favorite coding language is": "favourite_language",
            "my college is": "college",
            "i use": "device",
        }

        for trigger, key in memory_patterns.items():

            if trigger in text:

                value = prompt[prompt.lower().find(trigger) + len(trigger):].strip()

                self.profile.remember(key, value)

                return f"I'll remember that."

        questions = {
            "what is my name": "name",
            "what's my name": "name",
            "what is my favourite coding language": "favourite_language",
            "what is my favorite coding language": "favourite_language",
            "what is my favourite language": "favourite_language",
            "what is my college": "college",
            "which laptop do i use": "device",
            "what laptop do i use": "device",
        }

        for question, key in questions.items():

            if question in text:

                value = self.profile.recall(key)

                if value:
                    return value

                return "I don't know that yet."

        return None

    # --------------------------------------------------
    # FILE SEARCH
    # --------------------------------------------------

    def file_search(self, prompt):

        text = prompt.lower().strip()

        if not text.startswith("find "):
            return None

        keyword = prompt[5:].strip()

        results = self.search.search(keyword)

        if not results:
            return "No matching files found."

        message = "Found files:\n\n"

        for file in results[:10]:
            message += f"• {file}\n"

        return message

    # --------------------------------------------------
    # DESKTOP
    # --------------------------------------------------

    def desktop(self, prompt):

        text = prompt.lower()

        if "open chrome" in text:
            DesktopController.open_app("chrome")
            return "Opening Chrome..."

        if "open vscode" in text or "open vs code" in text:
            DesktopController.open_app("vscode")
            return "Opening VS Code..."

        if "open github" in text:
            DesktopController.open_website("https://github.com")
            return "Opening GitHub..."

        if "open youtube" in text:
            DesktopController.open_website("https://youtube.com")
            return "Opening YouTube..."

        return None

    # --------------------------------------------------

    def reply(self, prompt):

        prompt = prompt.strip()

        self.memory.add("user", prompt)
        self.add_history("user", prompt)

        for handler in (
            self.personal_memory,
            self.file_search,
            self.desktop,
        ):

            result = handler(prompt)

            if result:

                self.memory.add("assistant", result)
                self.add_history("assistant", result)

                return result

        response = self.llm.generate(prompt)

        self.memory.add("assistant", response)
        self.add_history("assistant", response)

        return response