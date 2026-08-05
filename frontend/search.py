"""
=========================================================
sAI V1 - Search Page
=========================================================
Web Search Interface
=========================================================
"""

from __future__ import annotations

import sys
import threading
from pathlib import Path

import customtkinter as ctk

# ---------------------------------------------------------
# Backend Import
# ---------------------------------------------------------

BACKEND = Path(__file__).resolve().parent.parent / "backend"

if str(BACKEND) not in sys.path:
    sys.path.append(str(BACKEND))

from search import SearchEngine


class SearchPage(ctk.CTkFrame):

    def __init__(self, master):

        super().__init__(master)

        self.engine = SearchEngine()

        self.build_ui()

    # --------------------------------------------------

    def build_ui(self):

        title = ctk.CTkLabel(
            self,
            text="Web Search",
            font=("Segoe UI", 28, "bold"),
        )

        title.pack(pady=(20, 10))

        self.entry = ctk.CTkEntry(
            self,
            placeholder_text="Search anything...",
            height=40,
        )

        self.entry.pack(
            fill="x",
            padx=20,
            pady=10,
        )

        self.entry.bind("<Return>", self.search)

        ctk.CTkButton(
            self,
            text="Search",
            width=150,
            command=self.search,
        ).pack(pady=5)

        self.output = ctk.CTkTextbox(
            self,
            wrap="word",
        )

        self.output.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20,
        )

    # --------------------------------------------------

    def log(self, text):

        self.output.insert("end", text + "\n")

        self.output.see("end")

    # --------------------------------------------------

    def search(self, event=None):

        query = self.entry.get().strip()

        if not query:
            return

        self.output.delete("1.0", "end")

        threading.Thread(
            target=self.run_search,
            args=(query,),
            daemon=True,
        ).start()

    # --------------------------------------------------

    def run_search(self, query):

        try:

            results = self.engine.web_search(query)

            if not results:

                self.log("No results found.")

                return

            for i, item in enumerate(results, start=1):

                self.log("=" * 70)

                self.log(f"Result {i}")

                self.log(f"Title : {item['title']}")

                self.log(f"URL   : {item['url']}")

                self.log(f"\n{item['body']}\n")

        except Exception as e:

            self.log(str(e))


if __name__ == "__main__":

    app = ctk.CTk()

    app.geometry("1000x700")

    SearchPage(app).pack(
        fill="both",
        expand=True,
    )

    app.mainloop()