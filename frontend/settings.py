"""
=========================================================
sAI V1 - Settings Page
=========================================================
"""

from __future__ import annotations

import customtkinter as ctk

from config import (
    ASSISTANT_NAME,
    VERSION,
    DEFAULT_PROVIDER,
    OLLAMA_MODEL,
    OPENAI_MODEL,
)


class SettingsPage(ctk.CTkFrame):

    def __init__(self, master):

        super().__init__(master)

        self.build_ui()

    # --------------------------------------------------

    def build_ui(self):

        title = ctk.CTkLabel(
            self,
            text="Settings",
            font=("Segoe UI", 24, "bold"),
        )

        title.pack(pady=(20, 10))

        info = ctk.CTkFrame(self)

        info.pack(fill="x", padx=20, pady=10)

        values = [
            ("Assistant", ASSISTANT_NAME),
            ("Version", VERSION),
            ("Default Provider", DEFAULT_PROVIDER),
            ("Ollama Model", OLLAMA_MODEL),
            ("OpenAI Model", OPENAI_MODEL),
        ]

        for key, value in values:

            row = ctk.CTkFrame(info)

            row.pack(fill="x", padx=10, pady=5)

            ctk.CTkLabel(
                row,
                text=key,
                width=180,
                anchor="w",
            ).pack(side="left", padx=5)

            ctk.CTkLabel(
                row,
                text=str(value),
                anchor="w",
            ).pack(side="left", padx=5)

        ctk.CTkButton(
            self,
            text="Save (Coming Soon)",
            state="disabled",
        ).pack(pady=20)


if __name__ == "__main__":

    app = ctk.CTk()

    app.geometry("700x500")

    SettingsPage(app).pack(fill="both", expand=True)

    app.mainloop()