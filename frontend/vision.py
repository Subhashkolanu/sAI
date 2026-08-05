"""
=========================================================
sAI V1 - Vision Page
=========================================================
Camera interface for sAI.
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

from vision import Vision


class VisionPage(ctk.CTkFrame):

    def __init__(self, master):

        super().__init__(master)

        self.vision = Vision()

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

        self.last_image = None

    # --------------------------------------------------

    def log(self, message):

        self.output.insert("end", message + "\n")

        self.output.see("end")

    # --------------------------------------------------

    def take_photo(self):

        try:

            path = self.vision.take_photo()

            self.last_image = path

            self.log(f"Saved:\n{path}")

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

            self.log("Take a photo first.")

            return

        try:

            text = self.vision.read_text(
                self.last_image,
            )

            self.log("\nOCR Result\n")

            self.log(text)

        except Exception as e:

            self.log(str(e))


if __name__ == "__main__":

    app = ctk.CTk()

    app.geometry("900x650")

    VisionPage(app).pack(
        fill="both",
        expand=True,
    )

    app.mainloop()