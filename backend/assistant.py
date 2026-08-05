"""
=========================================================
sAI V1 - Core Assistant
=========================================================
Main assistant logic responsible for routing user requests.
"""

from datetime import datetime
from rich import print

from llm import LLM


class Assistant:
    def __init__(self):
        self.llm = LLM()
        self.chat_history = []

    def _timestamp(self):
        return datetime.now().strftime("%H:%M:%S")

    def add_history(self, role: str, message: str):
        self.chat_history.append(
            {
                "role": role,
                "message": message,
                "time": self._timestamp(),
            }
        )

    def clear_history(self):
        self.chat_history.clear()

    def history(self):
        return self.chat_history

    def reply(self, prompt: str) -> str:
        prompt = prompt.strip()

        if not prompt:
            return "Please enter a message."

        self.add_history("user", prompt)

        try:
            response = self.llm.generate(prompt)

        except Exception as e:
            response = f"Error: {e}"

        self.add_history("assistant", response)

        return response

    def interactive(self):
        print("[bold cyan]sAI Chat Started[/bold cyan]")
        print("Type 'exit' to quit.\n")

        while True:

            user = input("You : ").strip()

            if user.lower() == "exit":
                break

            answer = self.reply(user)

            print(f"[green]sAI :[/green] {answer}")

        print("\nSession Ended.")