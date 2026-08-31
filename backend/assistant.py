"""
=========================================================
sAI V1 - Core Assistant
=========================================================
AI + Desktop + Personal Memory + File Search
=========================================================
"""

from __future__ import annotations

import re
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
    # HISTORY
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

        # ----------------------------------------------
        # Remember information
        # ----------------------------------------------

        memory_patterns = {
            "my name is": "name",
            "my favourite language is": "favourite_language",
            "my favorite language is": "favourite_language",
            "my favourite coding language is": "favourite_language",
            "my favorite coding language is": "favourite_language",
            "my college is": "college",
            "my city is": "city",
            "i use": "device",
        }

        for trigger, key in memory_patterns.items():

            if trigger in text:

                position = text.find(trigger)

                value = prompt[
                    position + len(trigger):
                ].strip()

                if not value:
                    return None

                # Don't treat arbitrary "I use..." sentences
                # as a device unless something follows it.
                self.profile.remember(key, value)

                return "I'll remember that."

        # ----------------------------------------------
        # Questions
        # ----------------------------------------------

        questions = {
            "what is my name": "name",
            "what's my name": "name",
            "what is my favourite coding language":
                "favourite_language",
            "what is my favorite coding language":
                "favourite_language",
            "what is my favourite language":
                "favourite_language",
            "what is my favorite language":
                "favourite_language",
            "what's my favourite language":
                "favourite_language",
            "what's my favorite language":
                "favourite_language",
            "what is my college": "college",
            "what's my college": "college",
            "what is my city": "city",
            "what's my city": "city",
            "which laptop do i use": "device",
            "what laptop do i use": "device",
            "which device do i use": "device",
            "what device do i use": "device",
        }

        for question, key in questions.items():

            if text == question:

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

        if not keyword:

            return "Please specify what you want me to find."

        try:

            results = self.search.search(keyword)

        except Exception as e:

            return f"File search error: {e}"

        if not results:

            return "No matching files found."

        message = "Found files:\n\n"

        for file in results[:10]:

            message += f"• {file}\n"

        return message.rstrip()

    # --------------------------------------------------
    # DESKTOP CONTROL
    # --------------------------------------------------

    def desktop(self, prompt):

        text = prompt.lower().strip()

        # ----------------------------------------------
        # Websites
        # ----------------------------------------------

        websites = {

            "github": "https://github.com",

            "youtube": "https://youtube.com",

            "google": "https://google.com",

        }

        for site, url in websites.items():

            patterns = (
                f"open {site}",
                f"launch {site}",
                f"start {site}",
                f"go to {site}",
            )

            if any(pattern in text for pattern in patterns):

                if DesktopController.open_website(url):

                    return f"Opening {site.title()}..."

                return f"Unable to open {site.title()}."

        # ----------------------------------------------
        # Folders
        # ----------------------------------------------

        folders = (
            "desktop",
            "downloads",
            "documents",
            "pictures",
            "videos",
            "music",
        )

        for folder in folders:

            patterns = (
                f"open {folder}",
                f"launch {folder}",
                f"open my {folder}",
                f"open the {folder}",
            )

            if any(pattern in text for pattern in patterns):

                if DesktopController.open_folder(folder):

                    return f"Opening {folder.title()}..."

                return f"Unable to open {folder.title()}."

        # ----------------------------------------------
        # Drives
        # ----------------------------------------------

        drive_match = re.search(
            r"\b(?:open|launch)\s+([a-zA-Z])\s*drive\b",
            text,
        )

        if drive_match:

            letter = drive_match.group(1)

            if DesktopController.open_drive(letter):

                return f"Opening {letter.upper()}: drive..."

            return f"{letter.upper()}: drive not found."

        # ----------------------------------------------
        # Applications
        # ----------------------------------------------

        available_apps = DesktopController.available_apps()

        # Check longer names first.
        available_apps = sorted(
            available_apps,
            key=len,
            reverse=True,
        )

        for app in available_apps:

            aliases = [
                app,
            ]

            for alias, target in DesktopController.ALIASES.items():

                if target == app:

                    aliases.append(alias)

            for alias in aliases:

                patterns = (
                    f"open {alias}",
                    f"launch {alias}",
                    f"start {alias}",
                    f"run {alias}",
                )

                if any(pattern in text for pattern in patterns):

                    if DesktopController.open_app(app):

                        return f"Opening {app.title()}..."

                    return (
                        f"{app.title()} is not installed "
                        "or could not be opened."
                    )

        return None

    # --------------------------------------------------
    # MAIN RESPONSE ROUTER
    # --------------------------------------------------

    def reply(self, prompt):

        prompt = prompt.strip()

        if not prompt:

            return "Please enter a message."

        # ----------------------------------------------
        # Store user message
        # ----------------------------------------------

        self.memory.add(
            "user",
            prompt,
        )

        self.add_history(
            "user",
            prompt,
        )

        # ----------------------------------------------
        # Built-in handlers
        # ----------------------------------------------

        for handler in (
            self.personal_memory,
            self.file_search,
            self.desktop,
        ):

            try:

                result = handler(prompt)

            except Exception as e:

                result = f"Error: {e}"

            if result:

                self.memory.add(
                    "assistant",
                    result,
                )

                self.add_history(
                    "assistant",
                    result,
                )

                return result

        # ----------------------------------------------
        # LLM
        # ----------------------------------------------

        try:

            response = self.llm.generate(prompt)

        except Exception as e:

            response = f"Error: {e}"

        self.memory.add(
            "assistant",
            response,
        )

        self.add_history(
            "assistant",
            response,
        )

        return response


# ------------------------------------------------------
# DIRECT TEST
# ------------------------------------------------------

if __name__ == "__main__":

    assistant = Assistant()

    print("sAI Assistant")
    print("Type 'exit' to quit.")
    print()

    while True:

        user = input("You: ").strip()

        if user.lower() == "exit":

            break

        response = assistant.reply(user)

        print(f"\nsAI: {response}\n")