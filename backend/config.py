"""
=========================================================
sAI V1 - Configuration
=========================================================
Central configuration file.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

from backend.storage import get_data_dir, maybe_run_migration

# ---------------------------------------------------------
# Load Environment Variables
# ---------------------------------------------------------

if getattr(sys, "frozen", False):
    BASE_DIR = Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))
else:
    BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

# ---------------------------------------------------------
# Project Directories
# ---------------------------------------------------------

BACKEND_DIR = BASE_DIR / "backend"
FRONTEND_DIR = BASE_DIR / "frontend"

ASSETS_DIR = BASE_DIR / "assets"
MODELS_DIR = BASE_DIR / "models"
SKILLS_DIR = BASE_DIR / "skills"
VOICE_DIR = BASE_DIR / "voice"
UI_DIR = BASE_DIR / "ui"

# User Data Directory (Precedence: SAI_DATA_DIR -> Packaged %LOCALAPPDATA% -> Source repo data/)
DATA_DIR = get_data_dir(BASE_DIR)
maybe_run_migration(DATA_DIR, BASE_DIR)

CACHE_DIR = DATA_DIR / "cache"
LOG_DIR = DATA_DIR / "logs"
MEMORY_DIR = DATA_DIR / "memory"
TEMP_DIR = DATA_DIR / "temp"
UPLOAD_DIR = DATA_DIR / "uploads"

# Create required user data folders automatically (guaranteed writable)
for directory in (
    DATA_DIR,
    CACHE_DIR,
    LOG_DIR,
    MEMORY_DIR,
    TEMP_DIR,
    UPLOAD_DIR,
):
    directory.mkdir(parents=True, exist_ok=True)

# Resource directories (created in development; may be read-only when packaged)
for directory in (
    ASSETS_DIR,
    MODELS_DIR,
):
    try:
        directory.mkdir(parents=True, exist_ok=True)
    except OSError:
        pass

# ---------------------------------------------------------
# Assistant
# ---------------------------------------------------------

APP_NAME = "sAI"
ASSISTANT_NAME = "sAI"
VERSION = "1.0.0"

SYSTEM_PROMPT = """You are sAI, a scalable, local-first artificial intelligence assistant.
You provide clear, accurate, and direct responses. You can use tools to perform desktop
actions, write code, solve problems, and search memory. Keep your answers concise, practical,
and helpful."""

# ---------------------------------------------------------
# LLM Providers
# ---------------------------------------------------------

DEFAULT_PROVIDER = os.getenv("SAI_PROVIDER", "ollama").lower()

# Ollama
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:4b-instruct-2507-q4_K_M")

# OpenAI Compatible
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Model Parameters
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2048"))

# ---------------------------------------------------------
# UI Settings
# ---------------------------------------------------------

THEME = os.getenv("THEME", "dark")
ACCENT_COLOR = "#1f538d"

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
WINDOW_TITLE = f"{ASSISTANT_NAME} — Scalable AI Interface v{VERSION}"

# ---------------------------------------------------------
# Memory Settings
# ---------------------------------------------------------

MEMORY_DB = MEMORY_DIR / "memory.db"
PROFILE_PATH = DATA_DIR / "profile.json"
MAX_MEMORY_RESULTS = 5

# ---------------------------------------------------------
# Server (for optional API / remote access)
# ---------------------------------------------------------

HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))

# ---------------------------------------------------------
# Voice Settings
# ---------------------------------------------------------

VOICE_ENABLED = os.getenv("VOICE_ENABLED", "false").lower() == "true"
VOICE_RATE = int(os.getenv("VOICE_RATE", "175"))
VOICE_VOLUME = float(os.getenv("VOICE_VOLUME", "0.9"))
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")

# ---------------------------------------------------------
# Vision Settings
# ---------------------------------------------------------

VISION_ENABLED = os.getenv("VISION_ENABLED", "true").lower() == "true"
OCR_LANGUAGES = ["en"]

# ---------------------------------------------------------
# Desktop Automation
# ---------------------------------------------------------

SAFE_MODE = os.getenv("SAFE_MODE", "true").lower() == "true"
ALLOWED_ACTIONS = [
    "open_app",
    "open_browser",
    "take_screenshot",
    "type_text",
    "press_key",
    "click",
    "read_file",
    "write_file",
    "search_files",
]

# ---------------------------------------------------------
# Logging
# ---------------------------------------------------------

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = LOG_DIR / "sai.log"

# ---------------------------------------------------------
# Terminal Banner
# ---------------------------------------------------------

BANNER = r"""
   _____         _____
  / ____|  /\   |_   _|
 | (___   /  \    | |
  \___ \ / /\ \   | |
  ____) / ____ \ _| |_
 |_____/_/    \_\_____|
"""
