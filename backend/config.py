"""
=========================================================
sAI V1 - Configuration
=========================================================
Central configuration file.
"""

from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

# ---------------------------------------------------------
# Load Environment Variables
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

# ---------------------------------------------------------
# Project Directories
# ---------------------------------------------------------

BACKEND_DIR = BASE_DIR / "backend"
FRONTEND_DIR = BASE_DIR / "frontend"

ASSETS_DIR = BASE_DIR / "assets"
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
SKILLS_DIR = BASE_DIR / "skills"
VOICE_DIR = BASE_DIR / "voice"
UI_DIR = BASE_DIR / "ui"

CACHE_DIR = DATA_DIR / "cache"
LOG_DIR = DATA_DIR / "logs"
MEMORY_DIR = DATA_DIR / "memory"
TEMP_DIR = DATA_DIR / "temp"
UPLOAD_DIR = DATA_DIR / "uploads"

# Create required folders automatically
for directory in (
    DATA_DIR,
    ASSETS_DIR,
    MODELS_DIR,
    CACHE_DIR,
    LOG_DIR,
    MEMORY_DIR,
    TEMP_DIR,
    UPLOAD_DIR,
):
    directory.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------
# Assistant
# ---------------------------------------------------------

APP_NAME = "sAI"
ASSISTANT_NAME = "sAI"
VERSION = "1.0.0"

WAKE_WORD = "hey sai"

# ---------------------------------------------------------
# Window
# ---------------------------------------------------------

WINDOW_TITLE = "sAI Assistant"

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 760

THEME = "dark"

ACCENT_COLOR = "#00BFFF"

# ---------------------------------------------------------
# Server
# ---------------------------------------------------------

HOST = "127.0.0.1"
PORT = 8000

# ---------------------------------------------------------
# AI
# ---------------------------------------------------------

DEFAULT_PROVIDER = os.getenv("DEFAULT_PROVIDER", "ollama")

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "qwen3:4b-instruct-2507-q4_K_M",
)

OPENAI_MODEL = os.getenv(
    "OPENAI_MODEL",
    "gpt-5.5",
)

OPENAI_API_KEY = os.getenv(
    "OPENAI_API_KEY",
    "",
)

SERPAPI_KEY = os.getenv(
    "SERPAPI_KEY",
    "",
)

TEMPERATURE = 0.7
MAX_TOKENS = 2048

# ---------------------------------------------------------
# Memory
# ---------------------------------------------------------

MEMORY_DB = MEMORY_DIR / "memory.db"

VECTOR_DB = MEMORY_DIR / "vector_db"

MAX_MEMORY_ITEMS = 5000

# ---------------------------------------------------------
# Search
# ---------------------------------------------------------

SEARCH_RESULTS = 5

# ---------------------------------------------------------
# Voice
# ---------------------------------------------------------

VOICE_RATE = 180
VOICE_VOLUME = 1.0

MIC_TIMEOUT = 5
MIC_PHRASE_LIMIT = 15

# ---------------------------------------------------------
# Vision
# ---------------------------------------------------------

CAMERA_INDEX = 0

# ---------------------------------------------------------
# Automation
# ---------------------------------------------------------

CHECK_INTERVAL = 2

# ---------------------------------------------------------
# Logging
# ---------------------------------------------------------

LOG_FILE = LOG_DIR / "sai.log"

# ---------------------------------------------------------
# Banner
# ---------------------------------------------------------

BANNER = f"""
==========================================
            {APP_NAME} v{VERSION}
==========================================
Project Directory
{BASE_DIR}
==========================================
"""