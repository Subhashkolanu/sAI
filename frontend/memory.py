"""
=========================================================
sAI V1 - Memory Page
=========================================================
Displays and manages conversation memory.
=========================================================
"""

from __future__ import annotations

import sys
from pathlib import Path

import customtkinter as ctk

# ---------------------------------------------------------
# Backend Import
# ---------------------------------------------------------

BACKEND = Path(__file__).resolve().parent.parent / "backend"

if str(BACKEND) not in sys.path:
    sys.path.append(str(BACKEND))

from memory import Memory


class MemoryPage(ctk.CTkFrame):

    def __init__(self, master):

        super().__init__(master)

        self.memory = Memory()

        self.build_ui()

        self.load_history()

    # --------------------------------------------------

    def build_ui(self):

        title = ctk.CTkLabel(
            self,
            text="Memory",
            font=("Segoe UI", 28, "bold"),
        )

        title.pack(pady=(20, 10))

        self.text = ctk.CTkTextbox(
            self,
            wrap="word",
        )

        self.text.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20,
        )

        buttons = ctk.CTkFrame(self)

        buttons.pack(pady=(0, 20))

        ctk.CTkButton(
            buttons,
            text="Refresh",
            width=130,
            command=self.load_history,
        ).grid(row=0, column=0, padx=8)

        ctk.CTkButton(
            buttons,
            text="Clear Memory",
            width=150,
            fg_color="red",
            hover_color="#b00020",
            command=self.clear_memory,
        ).grid(row=0, column=1, padx=8)

    # --------------------------------------------------

    def load_history(self):

        self.text.delete("1.0", "end")

        history = self.memory.all()

        if not history:

            self.text.insert(
                "end",
                "No conversation history found."
            )
            return

        for item in history:

            self.text.insert(
                "end",
                f"[{item['timestamp']}]\n"
                f"{item['role'].upper()}:\n"
                f"{item['message']}\n\n"
            )

    # --------------------------------------------------

    def clear_memory(self):

        self.memory.clear()

        self.load_history()


if __name__ == "__main__":

    app = ctk.CTk()

    app.geometry("900x650")

    MemoryPage(app).pack(
        fill="both",
        expand=True,
    )

    app.mainloop()