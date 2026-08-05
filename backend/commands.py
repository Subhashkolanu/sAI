"""
=========================================================
sAI V1 - Command Manager
=========================================================
Handles built-in commands and routes them to functions.
=========================================================
"""

from __future__ import annotations

from datetime import datetime
from typing import Callable

from assistant import Assistant


class CommandManager:

    def __init__(self, assistant: Assistant):

        self.assistant = assistant

        self.commands: dict[str, Callable] = {}

        self._register_defaults()

    # --------------------------------------------------

    def _register_defaults(self):

        self.register("help", self.help)

        self.register("about", self.about)

        self.register("time", self.time)

        self.register("date", self.date)

        self.register("clear", self.clear)

        self.register("history", self.history)

        self.register("exit", self.exit)

    # --------------------------------------------------

    def register(self, name: str, function: Callable):

        self.commands[name.lower()] = function

    # --------------------------------------------------

    def execute(self, text: str):

        command = text.strip().lower()

        if command in self.commands:

            return self.commands[command]()

        return None

    # --------------------------------------------------

    def help(self):

        return (
            "Available Commands\n\n"
            "help\n"
            "about\n"
            "time\n"
            "date\n"
            "history\n"
            "clear\n"
            "exit"
        )

    # --------------------------------------------------

    def about(self):

        return (
            "sAI V1\n"
            "Offline AI Assistant\n"
            "Supports Chat, Memory, Voice, Vision and Automation."
        )

    # --------------------------------------------------

    def time(self):

        return datetime.now().strftime("%I:%M:%S %p")

    # --------------------------------------------------

    def date(self):

        return datetime.now().strftime("%d %B %Y")

    # --------------------------------------------------

    def clear(self):

        self.assistant.clear_history()

        return "Conversation history cleared."

    # --------------------------------------------------

    def history(self):

        history = self.assistant.history()

        if not history:

            return "No conversation history."

        lines = []

        for item in history:

            lines.append(
                f"[{item['time']}] "
                f"{item['role']} : "
                f"{item['message']}"
            )

        return "\n".join(lines)

    # --------------------------------------------------

    def exit(self):

        return "__EXIT__"

    # --------------------------------------------------

    def available(self):

        return sorted(self.commands.keys())


if __name__ == "__main__":

    assistant = Assistant()

    manager = CommandManager(assistant)

    print(manager.help())

    print()

    print(manager.time())

    print()

    print(manager.date())