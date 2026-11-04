"""
=========================================================
sAI V1 - Memory Page
=========================================================
Displays conversation history.
=========================================================
"""

from __future__ import annotations

import threading

import customtkinter as ctk

from backend.memory import Memory


class MemoryPage(ctk.CTkFrame):
    HISTORY_BATCH_SIZE = 50

    def __init__(self, master, memory=None):
        super().__init__(master)

        self.memory = memory or Memory()
        self._load_token = 0

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
            command=self.load_history,
            width=130,
        ).grid(row=0, column=0, padx=10)

        ctk.CTkButton(
            buttons,
            text="Clear Memory",
            fg_color="red",
            hover_color="#B00020",
            command=self.clear_memory,
            width=150,
        ).grid(row=0, column=1, padx=10)

    def load_history(self):
        self._load_token += 1
        token = self._load_token

        self.text.delete("1.0", "end")
        self.text.insert("end", "Loading conversation history...")
        threading.Thread(
            target=self._fetch_history,
            args=(token,),
            daemon=True,
        ).start()

    def _fetch_history(self, token):
        try:
            history = self.memory.all()
            callback = lambda: self._begin_history_render(history, token)
        except Exception as exc:
            callback = lambda: self._show_history_error(str(exc), token)
        try:
            self.after(0, callback)
        except RuntimeError:
            pass

    def _show_history_error(self, error, token):
        if token != self._load_token:
            return
        self.text.delete("1.0", "end")
        self.text.insert("end", f"Unable to load conversation history: {error}")

    def _begin_history_render(self, history, token):
        if token != self._load_token:
            return

        self.text.delete("1.0", "end")

        if not history:
            self.text.insert(
                "end",
                "No conversation history found."
            )
            return

        self._render_history_batch(history, 0, token)

    def _render_history_batch(self, history, start, token):
        if token != self._load_token:
            return
        for item in history[start:start + self.HISTORY_BATCH_SIZE]:
            self.text.insert(
                "end",
                f"[{item['timestamp']}]\n"
                f"{item['role'].upper()}\n"
                f"{item['message']}\n\n"
            )
        next_start = start + self.HISTORY_BATCH_SIZE
        if next_start < len(history):
            self.after(1, lambda: self._render_history_batch(history, next_start, token))

    def clear_memory(self):
        self._load_token += 1
        self.memory.clear()
        self.load_history()


if __name__ == "__main__":
    app = ctk.CTk()
    app.geometry("900x650")
    MemoryPage(app).pack(fill="both", expand=True)
    app.mainloop()
