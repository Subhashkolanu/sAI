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
import json
import urllib.request
import urllib.error
from pathlib import Path
from urllib.parse import urlparse


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
)
from backend.settings import Settings


console = Console()


# ---------------------------------------------------------
# Ollama
# ---------------------------------------------------------

DEFAULT_OLLAMA_URL = "http://127.0.0.1:11434"


def ollama_running(base_url: str) -> bool:

    try:

        request = urllib.request.Request(
            f"{base_url.rstrip('/')}/api/tags",
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


def model_available(base_url: str, model: str) -> bool:

    try:

        request = urllib.request.Request(
            f"{base_url.rstrip('/')}/api/tags",
            method="GET",
        )

        with urllib.request.urlopen(
            request,
            timeout=3,
        ) as response:
            data = json.loads(response.read().decode("utf-8"))

        return model in {
            item.get("name")
            for item in data.get("models", [])
            if item.get("name")
        }

    except Exception:

        return False


# ---------------------------------------------------------


def start_ollama(base_url: str) -> bool:

    if base_url.rstrip("/") != DEFAULT_OLLAMA_URL:
        console.print(
            "[red]The configured Ollama endpoint is not running.[/red]\n"
            "Start the configured Ollama service manually, then try again."
        )
        return False

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

        if ollama_running(base_url):

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


def ensure_ollama(base_url: str, model: str) -> bool:

    if not ollama_running(base_url):

        if not start_ollama(base_url):

            return False

    else:

        console.print(
            "[green]Ollama is already running.[/green]"
        )

    # Check model

    if not model_available(base_url, model):

        console.print(
            f"\n[red]Model not found:[/red] {model}"
        )

        console.print(
            f"[yellow]Run:[/yellow] ollama pull {model}"
        )

        return False

    console.print(
        f"[green]Model ready:[/green] {model}"
    )

    return True


def ensure_provider(settings: Settings) -> bool:
    """Preflight only the provider selected in persistent settings."""
    config = settings.llm_config()
    provider = config["provider"]

    if provider == "ollama":
        return ensure_ollama(config["ollama_base_url"], config["ollama_model"])

    if provider == "openai_compatible":
        endpoint = config["openai_base_url"]
        parsed = urlparse(endpoint)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            console.print("[red]Invalid OpenAI-compatible endpoint in Settings.[/red]")
            return False
        console.print(
            "[green]OpenAI-compatible provider configured:[/green] "
            f"{endpoint} (model: {config['openai_model']})"
        )
        return True

    console.print(f"[red]Unknown configured provider:[/red] {provider}")
    return False


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

    if not ensure_provider(Settings()):

        console.print(
            "\n[red]sAI cannot start until the selected provider "
            "is configured.[/red]"
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
