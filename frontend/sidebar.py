"""Original sAI navigation sidebar."""
from __future__ import annotations

import customtkinter as ctk


class Sidebar(ctk.CTkFrame):
    def __init__(self, master, callback=None):
        super().__init__(master, width=220)
        self.callback = callback
        self.grid_propagate(False)
        self.build_ui()

    def build_ui(self):
        ctk.CTkLabel(self, text="sAI", font=("Segoe UI", 28, "bold")).pack(pady=(20, 5))
        ctk.CTkLabel(self, text="Offline AI Assistant", font=("Segoe UI", 13)).pack(pady=(0, 25))
        self.buttons = {}
        menu = [
            ("💬 Chat", "chat"), ("🎤 Voice", "voice"), ("👁 Vision", "vision"),
            ("🧠 Memory", "memory"), ("🌐 Search", "search"), ("⚙ Settings", "settings"),
            ("ℹ About", "about"),
        ]
        for text, page in menu:
            button = ctk.CTkButton(self, text=text, height=40, command=lambda name=page: self.change_page(name))
            button.pack(fill="x", padx=15, pady=6)
            self.buttons[page] = button
        ctk.CTkLabel(self, text="").pack(expand=True, fill="both")
        ctk.CTkLabel(self, text="Version 1.0.0", font=("Segoe UI", 11)).pack(pady=15)

    def change_page(self, page):
        if self.callback:
            self.callback(page)

    def disable(self):
        for button in self.buttons.values(): button.configure(state="disabled")

    def enable(self):
        for button in self.buttons.values(): button.configure(state="normal")

    def highlight(self, page):
        for name, button in self.buttons.items():
            button.configure(fg_color="#1F6AA5" if name == page else ("gray75", "gray25"))
