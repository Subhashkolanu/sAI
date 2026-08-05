"""
=========================================================
sAI V1 - Utility Functions
=========================================================
Common helper functions used throughout the project.
=========================================================
"""

from __future__ import annotations

import json
import logging
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from rich.console import Console

from config import LOG_FILE

console = Console()

# ---------------------------------------------------------
# Logging
# ---------------------------------------------------------

LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger("sAI")


# ---------------------------------------------------------
# Console
# ---------------------------------------------------------

def info(message: str):
    console.print(f"[cyan]{message}[/cyan]")


def success(message: str):
    console.print(f"[green]{message}[/green]")


def warning(message: str):
    console.print(f"[yellow]{message}[/yellow]")


def error(message: str):
    console.print(f"[red]{message}[/red]")


# ---------------------------------------------------------
# Logger
# ---------------------------------------------------------

def log(message: str):
    logger.info(message)


def log_error(message: str):
    logger.error(message)


# ---------------------------------------------------------
# JSON
# ---------------------------------------------------------

def load_json(file: str | Path, default=None):

    path = Path(file)

    if not path.exists():
        return {} if default is None else default

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(file: str | Path, data: Any):

    path = Path(file)

    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False,
        )


# ---------------------------------------------------------
# File Utilities
# ---------------------------------------------------------

def ensure_dir(path: str | Path):

    Path(path).mkdir(
        parents=True,
        exist_ok=True,
    )


def delete_file(path: str | Path):

    path = Path(path)

    if path.exists():
        path.unlink()


def copy_file(src: str | Path, dst: str | Path):

    shutil.copy2(src, dst)


# ---------------------------------------------------------
# Time
# ---------------------------------------------------------

def now():

    return datetime.now()


def timestamp():

    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ---------------------------------------------------------
# UUID
# ---------------------------------------------------------

def generate_id():

    return str(uuid.uuid4())


# ---------------------------------------------------------
# String Helpers
# ---------------------------------------------------------

def clean_text(text: str):

    return " ".join(text.strip().split())


def truncate(text: str, length: int = 100):

    if len(text) <= length:
        return text

    return text[:length] + "..."


# ---------------------------------------------------------
# Banner
# ---------------------------------------------------------

def banner():

    console.rule("[bold cyan]sAI Assistant[/bold cyan]")


# ---------------------------------------------------------
# Testing
# ---------------------------------------------------------

if __name__ == "__main__":

    banner()

    info("Information")

    success("Success")

    warning("Warning")

    error("Error")

    log("Utility module loaded.")

    print(generate_id())

    print(timestamp())