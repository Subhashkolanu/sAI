"""
=========================================================
sAI V1 - Main Desktop Application
=========================================================
"""

from __future__ import annotations

import sys
from pathlib import Path

import customtkinter as ctk

# ---------------------------------------------------------
# Backend Path
# ---------------------------------------------------------

BACKEND = Path(__file__).resolve().parent.parent / "backend"

if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

# ---------------------------------------------------------
# Frontend Imports
# ---------------------------------------------------------

from frontend.chat import ChatPanel
from frontend.sidebar import Sidebar
from frontend.settings import SettingsPage
from frontend.about import AboutPage
from frontend.voice import VoicePage
from frontend.vision import VisionPage
from frontend.memory import MemoryPage
from frontend.search import SearchPage

from backend.config import (
    WINDOW_TITLE,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    THEME,
)

# ---------------------------------------------------------

ctk.set_appearance_mode(THEME)
ctk.set_default_color_theme("blue")


class SAIApp(ctk.CTk):

    def __init__(self):

        super().__init__()

        self.title(WINDOW_TITLE)

        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

        self.minsize(1100, 700)

        self.protocol(
            "WM_DELETE_WINDOW",
            self.close,
        )

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # ---------------------------------------------

        self.sidebar = Sidebar(
            self,
            callback=self.change_page,
        )

        self.sidebar.grid(
            row=0,
            column=0,
            sticky="ns",
        )

        # ---------------------------------------------

        self.container = ctk.CTkFrame(
            self,
            corner_radius=0,
        )

        self.container.grid(
            row=0,
            column=1,
            sticky="nsew",
        )

        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # ---------------------------------------------

        self.pages = {}

        self.current_page = None

        self.create_pages()

        self.change_page("chat")

    # -------------------------------------------------

    def create_pages(self):

        self.pages = {

            "chat": ChatPanel(self.container),

            "voice": VoicePage(self.container),

            "vision": VisionPage(self.container),

            "memory": MemoryPage(self.container),

            "search": SearchPage(self.container),

            "settings": SettingsPage(self.container),

            "about": AboutPage(self.container),

        }

        for page in self.pages.values():

            page.grid(
                row=0,
                column=0,
                sticky="nsew",
            )    # -------------------------------------------------

    def change_page(self, page_name: str):

        if page_name not in self.pages:
            return

        if self.current_page is not None:
            self.current_page.grid_remove()

        self.current_page = self.pages[page_name]

        self.current_page.grid()

        self.sidebar.highlight(page_name)

        # Refresh pages if required
        if page_name == "memory":

            if hasattr(self.current_page, "load_history"):

                try:
                    self.current_page.load_history()
                except Exception:
                    pass

    # -------------------------------------------------

    def refresh_current_page(self):

        if self.current_page is None:
            return

        if hasattr(self.current_page, "refresh"):

            try:
                self.current_page.refresh()
            except Exception:
                pass

    # -------------------------------------------------

    def close(self):

        self.destroy()


# =========================================================
# Entry Point
# =========================================================

def main():

    app = SAIApp()

    app.mainloop()


if __name__ == "__main__":

    main()