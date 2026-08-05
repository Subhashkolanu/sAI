"""
=========================================================
sAI V1 - Voice Page
=========================================================
Voice interface for sAI.
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

from speech import SpeechEngine


class VoicePage(ctk.CTkFrame):

    def __init__(self, master):

        super().__init__(master)

        self.engine = SpeechEngine()

        self.listening = False

        self.build_ui()

    # --------------------------------------------------

    def build_ui(self):

        title = ctk.CTkLabel(
            self,
            text="Voice Assistant",
            font=("Segoe UI", 28, "bold"),
        )

        title.pack(pady=(20, 10))

        self.status = ctk.CTkLabel(
            self,
            text="Status : Idle",
            font=("Segoe UI", 15),
        )

        self.status.pack(pady=5)

        self.output = ctk.CTkTextbox(
            self,
            height=350,
            wrap="word",
        )

        self.output.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20,
        )

        button_frame = ctk.CTkFrame(self)

        button_frame.pack(pady=10)

        self.listen_btn = ctk.CTkButton(
            button_frame,
            text="🎤 Start Listening",
            width=180,
            command=self.start_listening,
        )

        self.listen_btn.grid(row=0, column=0, padx=10)

        self.test_btn = ctk.CTkButton(
            button_frame,
            text="🔊 Test Voice",
            width=150,
            command=self.test_voice,
        )

        self.test_btn.grid(row=0, column=1, padx=10)

    # --------------------------------------------------

    def log(self, text):

        self.output.insert("end", text + "\n")

        self.output.see("end")

    # --------------------------------------------------

    def listen(self):

        self.status.configure(text="Status : Listening...")

        self.log("Listening...")

        text = self.engine.listen()

        if text:

            self.log(f"You : {text}")

            self.engine.speak(text)

        else:

            self.log("No speech detected.")

        self.status.configure(text="Status : Idle")

        self.listening = False

    # --------------------------------------------------

    def start_listening(self):

        if self.listening:
            return

        self.listening = True

        threading.Thread(
            target=self.listen,
            daemon=True,
        ).start()

    # --------------------------------------------------

    def test_voice(self):

        self.engine.speak(
            "Hello. Voice engine is working correctly."
        )

        self.log("Voice test completed.")


if __name__ == "__main__":

    app = ctk.CTk()

    app.geometry("900x650")

    VoicePage(app).pack(
        fill="both",
        expand=True,
    )

    app.mainloop()