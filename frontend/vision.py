"""
=========================================================
sAI V1 - Vision Page
=========================================================
Camera interface for sAI.
=========================================================
"""

from __future__ import annotations

import threading

import customtkinter as ctk

from backend.vision import Vision


class VisionPage(ctk.CTkFrame):

    def __init__(self, master):

        super().__init__(master)

        self.vision = Vision()

        self.last_image = None

        self.build_ui()

    # --------------------------------------------------

    def build_ui(self):

        title = ctk.CTkLabel(
            self,
            text="Vision",
            font=("Segoe UI", 28, "bold"),
        )

        title.pack(pady=(20, 10))

        self.status = ctk.CTkLabel(
            self,
            text="Camera Ready",
        )

        self.status.pack(pady=5)

        self.output = ctk.CTkTextbox(
            self,
            wrap="word",
            height=350,
        )

        self.output.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=20,
        )

        buttons = ctk.CTkFrame(self)

        buttons.pack(pady=10)

        ctk.CTkButton(
            buttons,
            text="📷 Take Photo",
            width=160,
            command=self.take_photo,
        ).grid(row=0, column=0, padx=10)

        ctk.CTkButton(
            buttons,
            text="🎥 Open Camera",
            width=160,
            command=self.open_camera,
        ).grid(row=0, column=1, padx=10)

        ctk.CTkButton(
            buttons,
            text="📄 OCR",
            width=120,
            command=self.ocr_last,
        ).grid(row=0, column=2, padx=10)

    # --------------------------------------------------

    def log(self, message: str):

        self.output.insert("end", message + "\n")

        self.output.see("end")

    # --------------------------------------------------

    def take_photo(self):

        try:

            image = self.vision.take_photo()

            self.last_image = image

            self.log(f"Image saved:\n{image}")

        except Exception as e:

            self.log(str(e))

    # --------------------------------------------------

    def open_camera(self):

        threading.Thread(
            target=self.vision.preview,
            daemon=True,
        ).start()

    # --------------------------------------------------

    def ocr_last(self):

        if self.last_image is None:

            self.log("No image available.")

            return

        try:

            text = self.vision.read_text(
                self.last_image,
            )

            self.log("\n===== OCR RESULT =====\n")

            self.log(text)

        except Exception as e:

            self.log(str(e))

    # --------------------------------------------------

    def refresh(self):

        pass


if __name__ == "__main__":

    app = ctk.CTk()

    app.geometry("900x650")

    page = VisionPage(app)

    page.pack(fill="both", expand=True)

    app.mainloop()