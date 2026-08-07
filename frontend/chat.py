"""
=========================================================
sAI V1 - Chat Panel
=========================================================
Responsive Chat UI
- Background AI Thread
- Read-only Chat
- Thinking Indicator
=========================================================
"""

from __future__ import annotations

import threading

import customtkinter as ctk

from backend.assistant import Assistant


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

        self.chat_box.configure(state="disabled")

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

        self.status = ctk.CTkLabel(
            self,
            text="Ready",
            anchor="w",
        )

        self.status.grid(
            row=2,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=10,
            pady=(0, 8),
        )

        self.display_message(
            "sAI",
            "Welcome sAI\nHow can I help you today?"
        )

    # --------------------------------------------------

    def display_message(self, sender, message):

        self.chat_box.configure(state="normal")

        self.chat_box.insert(
            "end",
            f"{sender}: {message}\n\n"
        )

        self.chat_box.configure(state="disabled")

        self.chat_box.see("end")

    # --------------------------------------------------

    def send_message(self, event=None):

        prompt = self.input_box.get().strip()

        if not prompt:
            return

        self.display_message("You", prompt)

        self.input_box.delete(0, "end")

        self.input_box.configure(state="disabled")

        self.send_button.configure(state="disabled")

        self.status.configure(
            text="sAI is thinking..."
        )

        threading.Thread(
            target=self.generate_response,
            args=(prompt,),
            daemon=True,
        ).start()

    # --------------------------------------------------

    def generate_response(self, prompt):

        try:

            response = self.assistant.reply(prompt)

        except Exception as e:

            response = f"Error: {e}"

        self.after(
            0,
            lambda: self.finish_response(response)
        )

    # --------------------------------------------------

    def finish_response(self, response):

        self.display_message(
            "sAI",
            response,
        )

        self.input_box.configure(
            state="normal"
        )

        self.send_button.configure(
            state="normal"
        )

        self.status.configure(
            text="Ready"
        )

        self.input_box.focus()

    # --------------------------------------------------

    def clear(self):

        self.chat_box.configure(state="normal")

        self.chat_box.delete(
            "1.0",
            "end",
        )

        self.chat_box.configure(state="disabled")

    # --------------------------------------------------

    def insert_system_message(self, message):

        self.display_message(
            "System",
            message,
        )


if __name__ == "__main__":

    app = ctk.CTk()

    app.geometry("900x600")

    ChatPanel(app).pack(
        fill="both",
        expand=True,
    )

    app.mainloop()