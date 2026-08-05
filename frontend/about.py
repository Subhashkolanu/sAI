"""
=========================================================
sAI V1 - About Page
=========================================================
Displays project information.
=========================================================
"""

from __future__ import annotations

import customtkinter as ctk

from config import (
    ASSISTANT_NAME,
    VERSION,
    DEFAULT_PROVIDER,
)


class AboutPage(ctk.CTkFrame):

    def __init__(self, master):

        super().__init__(master)

        self.build_ui()

    # --------------------------------------------------

    def build_ui(self):

        title = ctk.CTkLabel(
            self,
            text=ASSISTANT_NAME,
            font=("Segoe UI", 32, "bold"),
        )

        title.pack(pady=(25, 10))

        version = ctk.CTkLabel(
            self,
            text=f"Version {VERSION}",
            font=("Segoe UI", 18),
        )

        version.pack()

        description = ctk.CTkTextbox(
            self,
            width=700,
            height=320,
            wrap="word",
        )

        description.pack(
            padx=20,
            pady=20,
            fill="both",
            expand=True,
        )

        description.insert(
            "end",
            f"""
{ASSISTANT_NAME} V1

An offline-first AI assistant built in Python.

Current Features
----------------
✓ Chat Interface
✓ SQLite Memory
✓ Local LLM Support (Ollama)
✓ OpenAI Support
✓ Voice Engine
✓ Vision Engine
✓ Web Search
✓ Automation
✓ File Manager
✓ Logger

Default AI Provider
-------------------
{DEFAULT_PROVIDER}

Upcoming Features
-----------------
• Agentic AI
• Long-Term Memory
• Local RAG
• Plugin System
• Multi-Agent Support
• Screen Understanding
• Smart Automation
• Android Companion
• Desktop Control
• AI Workspace

Developer
---------
Subhash

Project
-------
sAI
"""
        )

        description.configure(state="disabled")

        footer = ctk.CTkLabel(
            self,
            text="© 2026 sAI Project",
            font=("Segoe UI", 12),
        )

        footer.pack(pady=15)


if __name__ == "__main__":

    app = ctk.CTk()

    app.geometry("900x650")

    AboutPage(app).pack(
        fill="both",
        expand=True,
    )

    app.mainloop()