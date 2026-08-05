"""
=========================================================
sAI V1 - Central Logger
=========================================================
Central logging system used throughout the application.
=========================================================
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from rich.console import Console

from config import LOG_DIR

console = Console()

LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = Path(LOG_DIR) / "sai.log"

LOGGER_NAME = "sAI"

logger = logging.getLogger(LOGGER_NAME)

logger.setLevel(logging.INFO)

logger.propagate = False

if not logger.handlers:

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        "%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )

    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)


# ---------------------------------------------------------
# Logging Functions
# ---------------------------------------------------------

def debug(message: str):
    logger.debug(message)


def info(message: str):
    logger.info(message)
    console.print(f"[cyan]{message}[/cyan]")


def success(message: str):
    logger.info(message)
    console.print(f"[green]{message}[/green]")


def warning(message: str):
    logger.warning(message)
    console.print(f"[yellow]{message}[/yellow]")


def error(message: str):
    logger.error(message)
    console.print(f"[red]{message}[/red]")


def critical(message: str):
    logger.critical(message)
    console.print(f"[bold red]{message}[/bold red]")


def exception(message: str):
    logger.exception(message)
    console.print(f"[bold red]{message}[/bold red]")


# ---------------------------------------------------------
# Banner
# ---------------------------------------------------------

def startup():

    logger.info("=" * 60)
    logger.info("sAI Logger Started")
    logger.info("=" * 60)


def shutdown():

    logger.info("=" * 60)
    logger.info("sAI Logger Stopped")
    logger.info("=" * 60)


# ---------------------------------------------------------
# Test
# ---------------------------------------------------------

if __name__ == "__main__":

    startup()

    debug("Debug Message")

    info("Information")

    success("Success")

    warning("Warning")

    error("Error")

    critical("Critical Error")

    shutdown()