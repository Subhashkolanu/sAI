"""
=========================================================
sAI V1 Launcher
=========================================================
Application Entry Point
=========================================================
"""

from __future__ import annotations

import sys
import time
import subprocess
import urllib.request
import urllib.error
from pathlib import Path


# ---------------------------------------------------------
# Project Paths
# ---------------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parent

BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"


for directory in (BACKEND_DIR, FRONTEND_DIR):

    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))


# ---------------------------------------------------------
# Imports
# ---------------------------------------------------------

from rich.console import Console
from rich.panel import Panel

from backend.config import (
    BANNER,
    ASSISTANT_NAME,
    VERSION,
    HOST,
    OLLAMA_MODEL,
)


console = Console()


# ---------------------------------------------------------
# Ollama
# ---------------------------------------------------------

OLLAMA_URL = "http://127.0.0.1:11434"


def ollama_running() -> bool:

    try:

        request = urllib.request.Request(
            f"{OLLAMA_URL}/api/tags",
            method="GET",
        )

        with urllib.request.urlopen(
            request,
            timeout=2,
        ):

            return True

    except Exception:

        return False


# ---------------------------------------------------------


def model_available() -> bool:

    try:

        request = urllib.request.Request(
            f"{OLLAMA_URL}/api/tags",
            method="GET",
        )

        with urllib.request.urlopen(
            request,
            timeout=3,
        ) as response:

            data = response.read().decode("utf-8")

        return OLLAMA_MODEL in data

    except Exception:

        return False


# ---------------------------------------------------------


def start_ollama() -> bool:

    console.print(
        "[yellow]Ollama is not running. Starting Ollama...[/yellow]"
    )

    try:

        creation_flags = 0

        if sys.platform == "win32":

            creation_flags = (
                subprocess.CREATE_NO_WINDOW
            )

        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=creation_flags,
        )

    except Exception as exc:

        console.print(
            f"[red]Could not start Ollama:[/red] {exc}"
        )

        return False

    # Wait for Ollama

    for _ in range(15):

        if ollama_running():

            console.print(
                "[green]Ollama is ready.[/green]"
            )

            return True

        time.sleep(1)

    console.print(
        "[red]Ollama did not become ready.[/red]"
    )

    return False


# ---------------------------------------------------------


def ensure_ollama() -> bool:

    if not ollama_running():

        if not start_ollama():

            return False

    else:

        console.print(
            "[green]Ollama is already running.[/green]"
        )

    # Check model

    if not model_available():

        console.print(
            f"\n[red]Model not found:[/red] {OLLAMA_MODEL}"
        )

        console.print(
            f"[yellow]Run:[/yellow] ollama pull {OLLAMA_MODEL}"
        )

        return False

    console.print(
        f"[green]Model ready:[/green] {OLLAMA_MODEL}"
    )

    return True


# ---------------------------------------------------------
# Banner
# ---------------------------------------------------------


def print_banner():

    console.print(
        Panel.fit(
            f"[bold cyan]{ASSISTANT_NAME}[/bold cyan]\n"
            f"Version {VERSION}",
            title="sAI Launcher",
            border_style="cyan",
        )
    )


# ---------------------------------------------------------
# GUI
# ---------------------------------------------------------


def launch_gui():

    try:

        from app import main

        main()

    except Exception as exc:

        console.print(
            f"[red]Failed to launch GUI:[/red] {exc}"
        )


# ---------------------------------------------------------
# Terminal
# ---------------------------------------------------------


def launch_terminal():

    try:

        from main import SAI

        SAI().run()

    except Exception as exc:

        console.print(
            f"[red]Failed to launch Terminal:[/red] {exc}"
        )


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------


def main():

    console.clear()

    print(BANNER)

    print_banner()

    console.print(
        "\n[bold]Checking AI engine...[/bold]"
    )

    if not ensure_ollama():

        console.print(
            "\n[red]sAI cannot start until Ollama "
            "is ready.[/red]"
        )

        input("\nPress Enter to exit...")

        return

    while True:

        console.print(
            "\n[bold]Select Mode[/bold]"
        )

        console.print("1. Desktop GUI")
        console.print("2. Terminal")
        console.print("3. Exit")

        choice = input(
            "\nChoice: "
        ).strip()

        if choice == "1":

            launch_gui()

            break

        elif choice == "2":

            launch_terminal()

            break

        elif choice == "3":

            console.print(
                "\nGoodbye!\n"
            )

            break

        else:

            console.print(
                "[yellow]Invalid choice. Try again.[/yellow]"
            )


# ---------------------------------------------------------


if __name__ == "__main__":

    main()
