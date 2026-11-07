"""Configuración general, rutas y constantes de Anime-CMD."""
import os
import sys
from pathlib import Path

VERSION = "1.5.0"

# Directorio base de datos y cache (~/.anime)
HOME_DIR = Path.home()
ANIME_DIR = HOME_DIR / ".anime"
ANIME_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = ANIME_DIR / "history.db"
MPV_LOG_PATH = ANIME_DIR / "mpv_run.log"

# Headers HTTP comunes
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9",
}

# Estilos de color ANSI para consola
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"
PURPLE = "\033[0;35m"
RED = "\033[0;31m"
WHITE = "\033[1;37m"
GRAY = "\033[0;90m"
