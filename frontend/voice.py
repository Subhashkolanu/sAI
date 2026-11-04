"""
=========================================================
sAI V1 - Voice Assistant
=========================================================
Voice Control Page
- Speech Recognition
- AI Response
- Voice Output
=========================================================
"""

from __future__ import annotations

import threading

import customtkinter as ctk

from backend.assistant import Assistant


class VoicePage(ctk.CTkFrame):

    def __init__(self, master, assistant=None):

        super().__init__(master)

        self.assistant = assistant or Assistant()
        self.engine = None
        self.unavailable_reason = None
        self.listening = False

        self.build_ui()
        self.status.configure(text="Status : Initializing voice...")
        self.listen_button.configure(state="disabled")
        threading.Thread(target=self.initialize_engine, daemon=True).start()

    def initialize_engine(self):
        try:
            from backend.speech import SpeechEngine
            engine = SpeechEngine()
            reason = None
        except Exception:
            engine = None
            reason = "Install requirements-voice.txt to enable voice."
        try:
            self.after(0, lambda: self.finish_engine_initialization(engine, reason))
        except RuntimeError:
            pass

    def finish_engine_initialization(self, engine, reason):
        self.engine = engine
        self.unavailable_reason = reason
        if reason:
            self.status.configure(text=reason)
            return
        self.status.configure(text="Status : Ready")
        self.listen_button.configure(state="normal")

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
            text="Status : Ready",
            font=("Segoe UI", 16),
        )
        self.status.pack()

        self.output = ctk.CTkTextbox(
            self,
            wrap="word",
            height=420,
        )

        self.output.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20,
        )

        self.output.configure(state="disabled")

        self.listen_button = ctk.CTkButton(
            self,
            text="🎤 Start Listening",
            width=220,
            command=self.start_listening,
        )

        self.listen_button.pack(pady=10)

    # --------------------------------------------------

    def write(self, text):

        self.output.configure(state="normal")

        self.output.insert("end", text + "\n\n")

        self.output.configure(state="disabled")

        self.output.see("end")

    # --------------------------------------------------

    def start_listening(self):

        if self.engine is None:
            return

        if self.listening:
            return

        self.listening = True

        self.listen_button.configure(state="disabled")

        self.status.configure(
            text="Listening..."
        )

        threading.Thread(
            target=self.voice_loop,
            daemon=True,
        ).start()

    # --------------------------------------------------

    def voice_loop(self):

        try:

            spoken = self.engine.listen()

            if not spoken:

                self.after(
                    0,
                    lambda: self.finish(
                        "No speech detected."
                    )
                )
                return

            self.after(
                0,
                lambda: self.write(
                    f"You : {spoken}"
                )
            )

            response = self.assistant.reply(spoken)

            self.engine.speak(response)

            self.after(
                0,
                lambda: self.write(
                    f"sAI : {response}"
                )
            )

            self.after(
                0,
                lambda: self.finish(
                    "Ready"
                )
            )

        except Exception as e:

            self.after(
                0,
                lambda: self.finish(str(e))
            )

    # --------------------------------------------------

    def finish(self, status):

        self.status.configure(
            text=f"Status : {status}"
        )

        self.listen_button.configure(
            state="normal"
        )

        self.listening = False


if __name__ == "__main__":

    app = ctk.CTk()

    app.geometry("900x650")

    VoicePage(app).pack(
        fill="both",
        expand=True,
    )

    app.mainloop()
