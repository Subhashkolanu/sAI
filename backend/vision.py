"""
=========================================================
sAI V1 - Vision Engine
=========================================================
Features
- Open webcam
- Capture image
- Save screenshots
- Basic OCR
- Image information
=========================================================
"""

from __future__ import annotations

from pathlib import Path
from datetime import datetime

import cv2
import easyocr
from PIL import Image

from config import CAMERA_INDEX, UPLOAD_DIR


class Vision:
    def __init__(self):
        self.reader = easyocr.Reader(["en"], gpu=False)

    # --------------------------------------------------

    def capture(self):

        camera = cv2.VideoCapture(CAMERA_INDEX)

        if not camera.isOpened():
            raise RuntimeError("Unable to access webcam.")

        ok, frame = camera.read()

        camera.release()

        if not ok:
            raise RuntimeError("Unable to capture image.")

        return frame

    # --------------------------------------------------

    def show_camera(self):

        camera = cv2.VideoCapture(CAMERA_INDEX)

        if not camera.isOpened():
            raise RuntimeError("Unable to access webcam.")

        while True:

            ok, frame = camera.read()

            if not ok:
                break

            cv2.imshow("sAI Camera", frame)

            key = cv2.waitKey(1)

            if key == ord("q"):
                break

        camera.release()
        cv2.destroyAllWindows()

    # --------------------------------------------------

    def save_capture(self):

        frame = self.capture()

        filename = (
            UPLOAD_DIR
            / f"capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        )

        cv2.imwrite(str(filename), frame)

        return filename

    # --------------------------------------------------

    def read_text(self, image_path):

        results = self.reader.readtext(str(image_path))

        text = []

        for _, value, _ in results:
            text.append(value)

        return "\n".join(text)

    # --------------------------------------------------

    def image_info(self, image_path):

        img = Image.open(image_path)

        return {
            "width": img.width,
            "height": img.height,
            "mode": img.mode,
            "format": img.format,
        }

    # --------------------------------------------------

    def take_photo(self):

        path = self.save_capture()

        print(f"Image saved to:\n{path}")

        return path

    # --------------------------------------------------

    def preview(self):

        self.show_camera()


if __name__ == "__main__":

    vision = Vision()

    print("Vision Test")

    img = vision.take_photo()

    print(vision.image_info(img))

    print("\nOCR Result:\n")

    print(vision.read_text(img))