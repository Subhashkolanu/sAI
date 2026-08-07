"""
=========================================================
sAI V1 - Search Page
=========================================================
Search conversation history.
=========================================================
"""

from __future__ import annotations

import customtkinter as ctk

from backend.search import SearchEngine


class SearchPage(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master)

        self.engine = SearchEngine()

        title = ctk.CTkLabel(
            self,
            text="Search",
            font=("Segoe UI", 28, "bold"),
        )
        title.pack(pady=(20, 10))

        self.entry = ctk.CTkEntry(
            self,
            placeholder_text="Search conversations..."
        )
        self.entry.pack(fill="x", padx=20)

        ctk.CTkButton(
            self,
            text="Search",
            command=self.search
        ).pack(pady=10)

        self.results = ctk.CTkTextbox(self)
        self.results.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20,
        )

    def search(self):

        keyword = self.entry.get().strip()

        self.results.delete("1.0", "end")

        if not keyword:
            return

        data = self.engine.search(keyword)

        if not data:
            self.results.insert(
                "end",
                "No results found."
            )
            return

        for item in data:
            self.results.insert(
                "end",
                f"[{item['timestamp']}]\n"
                f"{item['role'].upper()}\n"
                f"{item['message']}\n\n"
            )


if __name__ == "__main__":
    app = ctk.CTk()
    app.geometry("900x650")
    SearchPage(app).pack(fill="both", expand=True)
    app.mainloop()