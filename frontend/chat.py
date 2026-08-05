"""
=========================================================
sAI V1 - Chat Panel
=========================================================
Chat interface component for the desktop GUI.
=========================================================
"""

from __future__ import annotations

import customtkinter as ctk

from assistant import Assistant


class ChatPanel(ctk.CTkFrame):

    def __init__(self, master):

        super().__init__(master)

        self.assistant = Assistant()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.build_ui()

    # --------------------------------------------------

    def build_ui(self):

        self.chat_box = ctk.CTkTextbox(
            self,
            wrap="word",
            font=("Consolas", 15),
        )

        self.chat_box.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="nsew",
            padx=10,
            pady=10,
        )

        self.input_box = ctk.CTkEntry(
            self,
            placeholder_text="Type your message...",
            height=40,
        )

        self.input_box.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=(10, 5),
            pady=(0, 10),
        )

        self.input_box.bind("<Return>", self.send_message)

        self.send_button = ctk.CTkButton(
            self,
            text="Send",
            width=100,
            command=self.send_message,
        )

        self.send_button.grid(
            row=1,
            column=1,
            padx=(5, 10),
            pady=(0, 10),
        )

        self.display_message(
            "sAI",
            "Welcome to sAI V1!\nHow can I help you today?",
        )

    # --------------------------------------------------

    def display_message(self, sender: str, message: str):

        self.chat_box.insert(
            "end",
            f"{sender}: {message}\n\n",
        )

        self.chat_box.see("end")

    # --------------------------------------------------

    def send_message(self, event=None):

        prompt = self.input_box.get().strip()

        if not prompt:
            return

        self.display_message("You", prompt)

        self.input_box.delete(0, "end")

        self.update()

        try:

            response = self.assistant.reply(prompt)

        except Exception as e:

            response = f"Error: {e}"

        self.display_message("sAI", response)

    # --------------------------------------------------

    def clear(self):

        self.chat_box.delete("1.0", "end")

    # --------------------------------------------------

    def insert_system_message(self, message: str):

        self.display_message("System", message)


if __name__ == "__main__":

    app = ctk.CTk()

    app.geometry("900x600")

    panel = ChatPanel(app)

    panel.pack(fill="both", expand=True)

    app.mainloop()