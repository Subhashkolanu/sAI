"""
=========================================================
sAI V1 Launcher
=========================================================
Application Entry Point
=========================================================
"""

from __future__ import annotations

import sys
from pathlib import Path

# ---------------------------------------------------------
# Project Paths
# ---------------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"

# Add project folders to Python path
for directory in (BACKEND_DIR, FRONTEND_DIR):
    if str(directory) not in sys.path:
        sys.path.insert(0, str(directory))

# ---------------------------------------------------------
# Imports
# ---------------------------------------------------------

from rich.console import Console
from rich.panel import Panel

from config import BANNER, ASSISTANT_NAME, VERSION

console = Console()


def print_banner():
    console.print(
        Panel.fit(
            f"[bold cyan]{ASSISTANT_NAME}[/bold cyan]\n"
            f"Version {VERSION}",
            title="sAI Launcher",
            border_style="cyan",
        )
    )


def launch_gui():
    try:
        from app import main
        main()
    except Exception as exc:
        console.print(f"[red]Failed to launch GUI:[/red] {exc}")


def launch_terminal():
    try:
        from main import SAI
        SAI().run()
    except Exception as exc:
        console.print(f"[red]Failed to launch Terminal:[/red] {exc}")


def main():
    console.clear()
    print(BANNER)
    print_banner()

    while True:
        console.print("\n[bold]Select Mode[/bold]")
        console.print("1. Desktop GUI")
        console.print("2. Terminal")
        console.print("3. Exit")

        choice = input("\nChoice: ").strip()

        if choice == "1":
            launch_gui()
            break

        elif choice == "2":
            launch_terminal()
            break

        elif choice == "3":
            console.print("\nGoodbye!\n")
            break

        else:
            console.print("[yellow]Invalid choice. Try again.[/yellow]")


if __name__ == "__main__":
    main()