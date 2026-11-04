"""sAI desktop application using the pre-Task-005 layout."""
from __future__ import annotations

import customtkinter as ctk

from backend.assistant import Assistant
from backend.config import WINDOW_HEIGHT, WINDOW_TITLE, WINDOW_WIDTH
from backend.settings import Settings
from frontend.about import AboutPage
from frontend.chat import ChatPanel
from frontend.memory import MemoryPage
from frontend.search import SearchPage
from frontend.settings import SettingsPage
from frontend.sidebar import Sidebar
from frontend.vision import VisionPage
from frontend.voice import VoicePage


class SAIApp(ctk.CTk):
    def __init__(self):
        self.settings = Settings()
        ctk.set_appearance_mode(self.settings.get("theme"))
        ctk.set_default_color_theme("blue")
        super().__init__()
        self.title(WINDOW_TITLE)
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.minsize(1100, 700)
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.assistant = Assistant()
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.sidebar = Sidebar(self, callback=self.change_page)
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.container = ctk.CTkFrame(self, corner_radius=0)
        self.container.grid(row=0, column=1, sticky="nsew")
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        self.create_pages()
        self.current_page = None
        self.pages["chat"].status.configure(text="Starting sAI...")
        self.change_page("chat")
        self.after(0, self.finish_startup)

    def create_pages(self):
        self.pages = {
            "chat": ChatPanel(self.container, assistant=self.assistant),
            "settings": SettingsPage(self.container, settings=self.settings, assistant=self.assistant, on_save=self.apply_settings),
            "about": AboutPage(self.container),
        }
        self.page_factories = {
            "voice": lambda: VoicePage(self.container, assistant=self.assistant),
            "vision": lambda: VisionPage(self.container),
            "memory": lambda: MemoryPage(self.container, memory=self.assistant.memory),
            "search": lambda: SearchPage(self.container, memory=self.assistant.memory),
        }
        for page in self.pages.values():
            page.grid(row=0, column=0, sticky="nsew")

    def change_page(self, page_name: str):
        if page_name == "voice":
            return
        if page_name not in self.pages and page_name in self.page_factories:
            self.pages[page_name] = self.page_factories[page_name]()
            self.pages[page_name].grid(row=0, column=0, sticky="nsew")
        if page_name not in self.pages:
            return
        if self.current_page is not None:
            self.current_page.grid_remove()
        self.current_page = self.pages[page_name]
        self.current_page.grid()
        self.sidebar.highlight(page_name)
        if hasattr(self.current_page, "load_history"):
            self.current_page.load_history()

    def finish_startup(self):
        self.pages["chat"].status.configure(text="Ready")

    def apply_settings(self):
        self.assistant.llm.settings.data = self.settings.llm_config()
        ctk.set_appearance_mode(self.settings.get("theme"))

    def close(self):
        self.assistant.close()
        self.destroy()


def main():
    app = SAIApp()
    app.mainloop()


if __name__ == "__main__":
    main()
