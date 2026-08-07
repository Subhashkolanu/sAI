"""
=========================================================
sAI V1 - Desktop Controller
=========================================================
Launches applications, folders and websites.
=========================================================
"""

from __future__ import annotations

import os
import subprocess
import webbrowser
from pathlib import Path


class DesktopController:

    APPS = {

        "chrome": [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ],

        "edge": [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        ],

        "vscode": [
            r"C:\Users\%USERNAME%\AppData\Local\Programs\Microsoft VS Code\Code.exe",
        ],

        "notepad": ["notepad"],

        "calculator": ["calc"],

        "paint": ["mspaint"],

        "explorer": ["explorer"],
    }

    # -------------------------------------------------

    @staticmethod
    def open_app(name: str):

        name = name.lower()

        if name not in DesktopController.APPS:
            return False

        for app in DesktopController.APPS[name]:

            app = os.path.expandvars(app)

            try:

                if Path(app).exists():

                    subprocess.Popen(app)

                    return True

            except Exception:
                pass

            try:

                subprocess.Popen(app)

                return True

            except Exception:
                pass

        return False

    # -------------------------------------------------

    @staticmethod
    def open_folder(folder: str):

        folder = folder.lower()

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

        os.startfile(folders[folder])

        return True

    # -------------------------------------------------

    @staticmethod
    def open_drive(letter: str):

        path = f"{letter.upper()}:\\"

        if Path(path).exists():

            os.startfile(path)

            return True

        return False

    # -------------------------------------------------

    @staticmethod
    def open_website(url: str):

        webbrowser.open(url)

        return True