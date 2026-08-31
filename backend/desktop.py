"""
=========================================================
sAI V1 - Desktop Controller
=========================================================
Launches applications, folders, drives and websites.
=========================================================
"""

from __future__ import annotations

import os
import shutil
import subprocess
import webbrowser
from pathlib import Path


class DesktopController:

    # --------------------------------------------------
    # APPLICATIONS
    # --------------------------------------------------

    APPS = {

        "chrome": [
            "chrome",
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ],

        "edge": [
            "msedge",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        ],

        "vscode": [
            "code",
            r"%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe",
        ],

        "opera": [
            "opera",
            r"%LOCALAPPDATA%\Programs\Opera\launcher.exe",
            r"C:\Program Files\Opera\launcher.exe",
            r"C:\Program Files (x86)\Opera\launcher.exe",
        ],

        "notepad": [
            "notepad",
        ],

        "calculator": [
            "calc",
        ],

        "paint": [
            "mspaint",
        ],

        "explorer": [
            "explorer",
        ],

        "cmd": [
            "cmd",
        ],

        "powershell": [
            "powershell",
        ],

        "terminal": [
            "wt",
        ],

        "word": [
            "winword",
        ],

        "excel": [
            "excel",
        ],

        "powerpoint": [
            "powerpnt",
        ],

        "spotify": [
            "spotify",
        ],

        "discord": [
            "discord",
        ],
    }

    # --------------------------------------------------
    # ALIASES
    # --------------------------------------------------

    ALIASES = {

        "google chrome": "chrome",
        "chrome browser": "chrome",

        "microsoft edge": "edge",
        "edge browser": "edge",

        "visual studio code": "vscode",
        "vs code": "vscode",
        "visual studio": "vscode",

        "opera browser": "opera",

        "file explorer": "explorer",
        "windows explorer": "explorer",

        "windows terminal": "terminal",

        "ms word": "word",
        "microsoft word": "word",

        "ms excel": "excel",
        "microsoft excel": "excel",

        "ms powerpoint": "powerpoint",
        "microsoft powerpoint": "powerpoint",
    }

    # --------------------------------------------------
    # NORMALIZE NAME
    # --------------------------------------------------

    @staticmethod
    def normalize_app_name(name: str) -> str:

        name = name.lower().strip()

        return DesktopController.ALIASES.get(
            name,
            name,
        )

    # --------------------------------------------------
    # OPEN APPLICATION
    # --------------------------------------------------

    @staticmethod
    def open_app(name: str) -> bool:

        name = DesktopController.normalize_app_name(name)

        if name not in DesktopController.APPS:
            return False

        candidates = DesktopController.APPS[name]

        for app in candidates:

            app = os.path.expandvars(app)

            # ------------------------------------------
            # Executable/path exists
            # ------------------------------------------

            if Path(app).exists():

                try:

                    subprocess.Popen(
                        [app],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )

                    return True

                except Exception:
                    pass

            # ------------------------------------------
            # Executable available through PATH
            # ------------------------------------------

            if shutil.which(app):

                try:

                    subprocess.Popen(
                        [app],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )

                    return True

                except Exception:
                    pass

            # ------------------------------------------
            # Windows shell fallback
            # ------------------------------------------

            try:

                subprocess.Popen(
                    ["cmd", "/c", "start", "", app],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )

                return True

            except Exception:
                pass

        return False

    # --------------------------------------------------
    # OPEN FOLDER
    # --------------------------------------------------

    @staticmethod
    def open_folder(folder: str) -> bool:

        folder = folder.lower().strip()

        home = Path.home()

        folders = {

            "desktop": home / "Desktop",

            "downloads": home / "Downloads",

            "documents": home / "Documents",

            "pictures": home / "Pictures",

            "videos": home / "Videos",

            "music": home / "Music",

        }

        if folder not in folders:
            return False

        path = folders[folder]

        if not path.exists():
            return False

        try:

            os.startfile(path)

            return True

        except Exception:

            return False

    # --------------------------------------------------
    # OPEN DRIVE
    # --------------------------------------------------

    @staticmethod
    def open_drive(letter: str) -> bool:

        letter = letter.strip().replace(":", "").upper()

        if len(letter) != 1:
            return False

        path = f"{letter}:\\"

        if not Path(path).exists():
            return False

        try:

            os.startfile(path)

            return True

        except Exception:

            return False

    # --------------------------------------------------
    # OPEN WEBSITE
    # --------------------------------------------------

    @staticmethod
    def open_website(url: str) -> bool:

        try:

            webbrowser.open(url)

            return True

        except Exception:

            return False

    # --------------------------------------------------
    # CHECK APPLICATION
    # --------------------------------------------------

    @staticmethod
    def is_available(name: str) -> bool:

        name = DesktopController.normalize_app_name(name)

        if name not in DesktopController.APPS:
            return False

        for app in DesktopController.APPS[name]:

            app = os.path.expandvars(app)

            if Path(app).exists():
                return True

            if shutil.which(app):
                return True

        return False

    # --------------------------------------------------
    # AVAILABLE APPLICATIONS
    # --------------------------------------------------

    @staticmethod
    def available_apps() -> list[str]:

        return sorted(
            DesktopController.APPS.keys()
        )


# ------------------------------------------------------
# TEST
# ------------------------------------------------------

if __name__ == "__main__":

    print("sAI Desktop Controller")
    print("-----------------------")

    print("\nAvailable applications:")

    for app in DesktopController.available_apps():

        status = (
            "Available"
            if DesktopController.is_available(app)
            else "Not detected"
        )

        print(f"{app:15} : {status}")