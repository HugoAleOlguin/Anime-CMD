"""Utilidades visuales, banners y tarjetas TUI minimalistas para Anime-CMD."""
import os
import sys
from typing import Optional
from src.core.config import VERSION
from src.core.models import HistoryEntry
from src.ui.theme import (
    RESET, BOLD, DIM, CYAN, PURPLE, BLUE, ORANGE, GREEN, RED, GRAY, WHITE
)

def clear_screen():
    """Limpia la pantalla de la terminal para una experiencia visual limpia y directa."""
    if sys.platform == "win32":
        os.system("cls")
    else:
        os.system("clear")

def print_unified_card(entry: Optional[HistoryEntry] = None):
    """Muestra el marco unificado, sobrio y estilizado de Anime-CMD con descripción y atajos."""
    width = 68
    header_title = f"── ▶ ANIME-CMD v{VERSION} "
    dash_count = width - len(header_title)
    border_top = f"{PURPLE}╭{header_title}{'─' * max(0, dash_count)}╮{RESET}"
    border_bot = f"{PURPLE}╰{'─' * width}╯{RESET}"
    empty_line = f"{PURPLE}│{' ' * width}│{RESET}"

    print(border_top)
    print(empty_line)

    l1 = "  Reproductor de anime para la terminal, rápido y sin anuncios."
    print(f"{PURPLE}│{RESET}{WHITE}{l1}{RESET}{' ' * max(0, width - len(l1))}{PURPLE}│{RESET}")

    l2 = "  Audio latino, castellano y subtitulado en japonés."
    print(f"{PURPLE}│{RESET}{GRAY}{l2}{RESET}{' ' * max(0, width - len(l2))}{PURPLE}│{RESET}")
    print(empty_line)

    if entry:
        title = entry.anime_title
        if len(title) > 46:
            title = title[:43] + "..."
        l_cont = f"  {CYAN}▶{RESET} {BOLD}Continuar:{RESET} {WHITE}{title}{RESET}"
        l_cont_raw = f"  ▶ Continuar: {title}"
        print(f"{PURPLE}│{RESET}{l_cont}{' ' * max(0, width - len(l_cont_raw))}{PURPLE}│{RESET}")

        ep_pos = f"    Capítulo {entry.last_episode}  •  {entry.progress}"
        print(f"{PURPLE}│{RESET}{GRAY}{ep_pos}{RESET}{' ' * max(0, width - len(ep_pos))}{PURPLE}│{RESET}")
        print(empty_line)

    action_label = "[ENTER] Reanudar" if entry else "[Escribe] Buscar"
    styled_shortcuts = (
        f"  {GRAY}•{RESET} {CYAN}{action_label}{RESET}   "
        f"{GRAY}•{RESET} {BLUE}[-c] Comandos{RESET}   "
        f"{GRAY}•{RESET} {GRAY}[Ctrl+C] Salir{RESET}"
    )
    shortcuts_raw = f"  • {action_label}   • [-c] Comandos   • [Ctrl+C] Salir"
    print(f"{PURPLE}│{RESET}{styled_shortcuts}{' ' * max(0, width - len(shortcuts_raw))}{PURPLE}│{RESET}")
    print(border_bot)
    print()

def print_quick_resume(entry: HistoryEntry):
    """Alias compatible para invocar la tarjeta unificada."""
    print_unified_card(entry)

def print_banner():
    """Muestra el banner informativo para la pantalla de ayuda."""
    width = 64
    border_top = f"{GRAY}╭{'─' * width}╮{RESET}"
    border_bot = f"{GRAY}╰{'─' * width}╯{RESET}"

    l1_text = f"  ▶ ANIME-CMD v{VERSION} • Motor Agregador Multi-Plataforma"
    l1_pad = width - len(l1_text)
    line1 = f"{GRAY}│{RESET}  {CYAN}▶{RESET} {BOLD}{WHITE}ANIME-CMD{RESET} {PURPLE}v{VERSION}{RESET} {GRAY}•{RESET} {WHITE}Motor Agregador Multi-Plataforma{RESET}{' ' * l1_pad}{GRAY}│{RESET}"

    l2_text = "  ★ Doblaje Latino Prioritario │ [CAST] Castellano │ [SUB] Jap"
    l2_pad = width - len(l2_text)
    line2 = f"{GRAY}│{RESET}  {CYAN}★{RESET} {GREEN}Doblaje Latino Prioritario{RESET} {GRAY}│{RESET} {BLUE}[CAST]{RESET} Castellano {GRAY}│{RESET} {ORANGE}[SUB]{RESET} Jap{' ' * l2_pad}{GRAY}│{RESET}"

    print(border_top)
    print(line1)
    print(line2)
    print(border_bot)
    print()

def print_help():
    """Muestra la pantalla de ayuda estilizada."""
    print(f"\n    {CYAN}{BOLD}Uso:{RESET} {WHITE}anime [opciones] [búsqueda]{RESET}\n")
    print(f"    {PURPLE}{BOLD}Opciones y Comandos:{RESET}")
    print(f"      {CYAN}-s, --sub{RESET}             Forzar versión en japonés subtitulada [SUB]")
    print(f"      {CYAN}-c, -h, --help{RESET}        Ver todos los comandos y ayuda")
    print(f"      {CYAN}-r, --resume{RESET}          Reanudar directamente el último anime visto")
    print(f"      {CYAN}-u, --update{RESET}          Actualizar Anime-CMD a la última versión")
    print(f"      {CYAN}-v, --version{RESET}         Mostrar versión instalada\n")
    print(f"    {PURPLE}{BOLD}Características del motor v{VERSION}:{RESET}")
    print(f"      {GRAY}•{RESET} {GREEN}Motor Multi-Proveedor:{RESET} Anime Online Ninja, TioAnime, MonosChinos, JKAnime.")
    print(f"      {GRAY}•{RESET} {GREEN}Separadores de Temporada:{RESET} Títulos de capítulos y navegación inteligente.")
    print(f"      {GRAY}•{RESET} {GREEN}Binario Autónomo:{RESET} Ejecución nativa sin dependencias de Python ni runtime.")
    print(f"      {GRAY}•{RESET} {GREEN}Evasión de Señuelos:{RESET} Resolución concurrente de streams activos.\n")

def print_version():
    print(f"Anime-CMD {PURPLE}v{VERSION}{RESET} {GRAY}•{RESET} Motor Agregador Nativo")

def print_error(msg: str):
    print(f"{RED}[ERROR]{RESET} {msg}")

def print_info(msg: str):
    print(f"{CYAN}[+]{RESET} {msg}")

def print_warn(msg: str):
    print(f"{ORANGE}[!]{RESET} {msg}")
