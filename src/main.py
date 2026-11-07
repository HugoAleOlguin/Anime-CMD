"""Punto de entrada principal de Anime-CMD con TUI moderna y Quick-Resume."""
import os
import sys

# Asegurar que la raíz del proyecto esté en sys.path para ejecuciones directas: python src/main.py
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Configurar codificación UTF-8 universal para evitar errores charmap/cp1252 en Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stdin, "reconfigure"):
    sys.stdin.reconfigure(encoding="utf-8", errors="replace")

# Habilitar soporte de secuencias de color ANSI en la consola de Windows
if sys.platform == "win32":
    os.system("")

import re
import argparse
from typing import Optional, List
from src.core.config import VERSION
from src.core.models import HistoryEntry, EpisodeItem
from src.core.db import DatabaseManager
from src.core.player import MPVPlayer
from src.providers.registry import ProviderRegistry
from src.extractors.registry import ExtractorRegistry
from src.ui.fzf import FZFSelector
from src.ui.theme import CYAN, BOLD, RESET, PURPLE, GRAY
from src.ui.printer import (
    clear_screen, print_unified_card, print_quick_resume, print_banner,
    print_help, print_version, print_info, print_warn, print_error
)

def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-s", "--sub", action="store_true", help="Forzar subtitulado")
    parser.add_argument("-r", "--resume", "--continue", "--continue-watch", dest="continue_watch", action="store_true", help="Reanudar último anime")
    parser.add_argument("-c", "-h", "--help", "--comandos", dest="help", action="store_true", help="Mostrar ayuda y comandos")
    parser.add_argument("-hh", dest="secret_mode", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("-u", "--update", action="store_true", help="Actualizar anime")
    parser.add_argument("-v", "--version", action="store_true", help="Mostrar versión")
    parser.add_argument("query", nargs="*", help="Término de búsqueda")

    args = parser.parse_args()

    if args.help:
        print_help()
        return

    if args.version:
        print_version()
        return

    db = DatabaseManager()
    fzf = FZFSelector()
    player = MPVPlayer()
    provider_reg = ProviderRegistry()
    extractor_reg = ExtractorRegistry()

    # Modo Reanudar explícito (-c)
    if args.continue_watch:
        last = db.get_last_watched(include_secret=bool(args.secret_mode))
        if not last:
            print_warn("No hay ningún anime en el historial para reanudar.")
            return

        print_info(f"Reanudando {last.anime_title} (Capítulo {last.last_episode}, Posición {last.progress})...")
        flow_res = play_flow(
            anime_title=last.anime_title,
            anime_url=last.url,
            provider_id=last.provider,
            episode_num=last.last_episode,
            start_pos=last.progress,
            db=db,
            fzf=fzf,
            player=player,
            provider_reg=provider_reg,
            extractor_reg=extractor_reg,
            force_sub=args.sub,
            secret_mode=bool(args.secret_mode or getattr(last, "is_secret", False) or last.provider == "secret")
        )
        if flow_res not in ("SEARCH", "BACK"):
            return

    initial_search = " ".join(args.query).strip() if args.query else None
    secret_mode = bool(args.secret_mode)

    # Bucle principal de navegación interactiva
    while True:
        if initial_search:
            search_term = initial_search
            initial_search = None
        else:
            clear_screen()
            last = db.get_last_watched(include_secret=secret_mode)
            print_unified_card(last)
            try:
                prompt_symbol = f"{PURPLE}▶{RESET}" if secret_mode else f"{CYAN}▶{RESET}"
                prompt_text = f"{prompt_symbol} {BOLD}Buscar anime{' secreto' if secret_mode else ''}:{RESET} "
                search_term = input(prompt_text).strip()
            except (KeyboardInterrupt, EOFError):
                print("\n¡Hasta la próxima!")
                return

            if not search_term:
                if last:
                    # El usuario pulsó ENTER directamente -> activar reanudación rápida
                    print_info(f"Reanudando {last.anime_title} (Capítulo {last.last_episode}, Posición {last.progress})...")
                    flow_res = play_flow(
                        anime_title=last.anime_title,
                        anime_url=last.url,
                        provider_id=last.provider,
                        episode_num=last.last_episode,
                        start_pos=last.progress,
                        db=db,
                        fzf=fzf,
                        player=player,
                        provider_reg=provider_reg,
                        extractor_reg=extractor_reg,
                        force_sub=args.sub,
                        secret_mode=bool(secret_mode or getattr(last, "is_secret", False) or last.provider == "secret")
                    )
                    if flow_res in ("SEARCH", "BACK"):
                        continue
                    return
                else:
                    return

        if search_term.lower() in ("salir", "exit", "quit", ":q"):
            print("¡Hasta la próxima!")
            return

        if search_term.lower() in ("-c", "-h", "--help", "--comandos", "comandos", "ayuda", "help"):
            print_help()
            return

        # Activar modo secreto si se escribió -hh en la búsqueda interactiva
        if search_term.startswith("-hh"):
            secret_mode = True
            search_term = search_term[3:].strip()
            if not search_term:
                clear_screen()
                last = db.get_last_watched(include_secret=True)
                print_unified_card(last)
                try:
                    search_term = input(f"{PURPLE}▶{RESET} {BOLD}Buscar anime secreto:{RESET} ").strip()
                except (KeyboardInterrupt, EOFError):
                    continue
                if not search_term and last:
                    print_info(f"Reanudando {last.anime_title} (Capítulo {last.last_episode}, Posición {last.progress})...")
                    flow_res = play_flow(
                        anime_title=last.anime_title,
                        anime_url=last.url,
                        provider_id=last.provider,
                        episode_num=last.last_episode,
                        start_pos=last.progress,
                        db=db,
                        fzf=fzf,
                        player=player,
                        provider_reg=provider_reg,
                        extractor_reg=extractor_reg,
                        force_sub=args.sub,
                        secret_mode=True
                    )
                    if flow_res in ("SEARCH", "BACK"):
                        continue
                    return

        if not search_term:
            continue

        if secret_mode:
            print_info(f"Consultando servidor secreto para '{search_term}'...")
        else:
            print_info(f"Buscando '{search_term}' en todos los servidores disponibles...")
        results = provider_reg.search_all(search_term, force_sub=args.sub, secret_mode=secret_mode)

        if not results:
            print_warn(f"No se encontraron animes para '{search_term}'.")
            try:
                input(f"{GRAY}Presiona ENTER para buscar de nuevo...{RESET}")
            except Exception:
                pass
            continue

        # Nivel 1: Selección de anime desde resultados
        back_to_search_prompt = False
        while True:
            options = [r.format_menu_line() for r in results]
            selected_line = fzf.select(
                options,
                prompt="  ❯ ",
                header=f"'{search_term}' • ↑/↓/TAB: Navegar • ENTER: Elegir • ESC: Volver a buscar"
            )
            if not selected_line:
                # El usuario pulsó ESC en la lista de animes -> Volver al buscador
                back_to_search_prompt = True
                break

            parts = selected_line.split("\t")
            if len(parts) < 3:
                print_error("Error al procesar la selección.")
                continue

            anime_title = parts[3] if len(parts) > 3 else re.sub(r"^(?:[^\w\s]*\s*\[[^\]]+\]\s*)+", "", parts[0]).strip(" │\t")
            anime_url = parts[1]
            provider_id = parts[2]

            prov = provider_reg.get(provider_id)
            if not prov:
                print_error(f"Proveedor '{provider_id}' no reconocido.")
                continue

            print_info(f"Cargando lista de capítulos de '{anime_title}'...")
            episodes = prov.get_episodes(anime_url)
            if not episodes:
                print_error("No se pudieron cargar los capítulos del anime seleccionado.")
                continue

            # Nivel 2: Selección de capítulo
            short_title = (anime_title[:24] + "...") if len(anime_title) > 27 else anime_title
            back_to_anime_list = False

            while True:
                anime_history = db.get_anime(anime_title)
                last_ep = anime_history.last_episode if anime_history else None
                episode_options = [ep.format_menu_line(current_watched_ep=last_ep) for ep in episodes]

                selected_ep = fzf.select(
                    episode_options,
                    prompt="  ❯ ",
                    header=f"{short_title} • ↑/↓/TAB: Navegar • ENTER: Ver • ESC: Volver a animes"
                )
                if not selected_ep:
                    # El usuario pulsó ESC en la lista de episodios -> Volver a la lista de animes
                    back_to_anime_list = True
                    break

                ep_parts = selected_ep.split("\t")
                if len(ep_parts) > 1 and ep_parts[1] == "HEADER":
                    continue  # Click en separador de temporada

                ep_url = ep_parts[1] if len(ep_parts) > 1 else anime_url
                ep_num = ep_parts[2] if len(ep_parts) > 2 else "1"

                # Nivel 3: Reproducción y menú posterior
                flow_res = play_flow(
                    anime_title=anime_title,
                    anime_url=anime_url,
                    provider_id=provider_id,
                    episode_num=ep_num,
                    start_pos="00:00:00",
                    db=db,
                    fzf=fzf,
                    player=player,
                    provider_reg=provider_reg,
                    extractor_reg=extractor_reg,
                    force_sub=args.sub,
                    episodes=episodes,
                    initial_ep_url=ep_url,
                    secret_mode=secret_mode
                )

                if flow_res == "EXIT":
                    return
                elif flow_res == "SEARCH":
                    back_to_search_prompt = True
                    break
                elif flow_res == "BACK":
                    # Volver a la lista de episodios de este anime
                    continue
                else:
                    continue

            if back_to_search_prompt:
                break
            if back_to_anime_list:
                continue

        if back_to_search_prompt:
            continue

def play_flow(
    anime_title: str,
    anime_url: str,
    provider_id: str,
    episode_num: str,
    start_pos: str,
    db: DatabaseManager,
    fzf: FZFSelector,
    player: MPVPlayer,
    provider_reg: ProviderRegistry,
    extractor_reg: ExtractorRegistry,
    force_sub: bool,
    episodes: Optional[List[EpisodeItem]] = None,
    initial_ep_url: Optional[str] = None,
    secret_mode: bool = False
):
    prov = provider_reg.get(provider_id)
    if not prov:
        print_error(f"Proveedor '{provider_id}' no disponible.")
        return

    # Si venimos de reanudar (-c o quick-resume), cargar episodios si no fueron provistos
    if not episodes:
        print_info(f"Cargando capítulos de '{anime_title}'...")
        episodes = prov.get_episodes(anime_url)

    # Construir mapa de capítulos: número -> EpisodeItem
    ep_map = {}
    if episodes:
        for ep in episodes:
            if not ep.is_season_header and ep.number.isdigit():
                ep_map[int(ep.number)] = ep

    current_ep = int(episode_num) if episode_num.isdigit() else 1
    current_pos = start_pos
    current_ep_url = initial_ep_url

    while True:
        # Resolver URL del capítulo actual
        if current_ep_url:
            target_url = current_ep_url
            current_ep_url = None  # Consumido para la primera iteración
        elif current_ep in ep_map:
            target_url = ep_map[current_ep].url
        else:
            target_url = anime_url

        pref_audio = "sub" if force_sub else "latino"
        print_info(f"Obteniendo transmisión para {anime_title} - Capítulo {current_ep}...")

        embeds = prov.get_embed_urls(target_url, pref_audio=pref_audio, episode_num=current_ep)
        stream_sources = extractor_reg.resolve_candidates(embeds)

        short_title = (anime_title[:24] + "...") if len(anime_title) > 27 else anime_title

        if not stream_sources:
            print_error(f"No se pudo extraer una fuente de reproducción activa para el capítulo {current_ep}.")
            action = fzf.select(
                ["🔄 Reintentar este capítulo", "📋 Cambiar capítulo", "❌ Salir"],
                prompt="  ❯ ",
                header=f"{short_title} Error • ↑/↓/TAB: Elegir • ENTER: Aceptar"
            )
            if action and "Reintentar" in action:
                continue
            elif action and "Cambiar" in action and episodes:
                anime_history = db.get_anime(anime_title)
                last_ep = str(current_ep) or (anime_history.last_episode if anime_history else None)
                episode_options = [ep.format_menu_line(current_watched_ep=last_ep) for ep in episodes]
                while True:
                    sel = fzf.select(
                        episode_options,
                        prompt="  ❯ ",
                        header=f"{short_title} • ↑/↓/TAB: Navegar • ENTER: Ver • ESC: Salir"
                    )
                    if not sel:
                        break
                    p = sel.split("\t")
                    if len(p) > 1 and p[1] == "HEADER":
                        continue
                    if len(p) > 2 and p[2].isdigit():
                        current_ep = int(p[2])
                        current_ep_url = p[1]
                        current_pos = "00:00:00"
                        break
                continue
            break

        media_title = f"{anime_title} - Capítulo {current_ep}"
        playback_success = False
        final_pos = current_pos or "00:00:00"

        for idx, stream_source in enumerate(stream_sources):
            print_info(f"Iniciando reproducción con MPV ({stream_source.server_name})...")

            # Registrar de inmediato en la base de datos para que figure como último visto
            try:
                is_sec = bool(secret_mode or provider_id == "secret")
                db.save_progress(HistoryEntry(
                    anime_title=anime_title,
                    url=anime_url,
                    provider=provider_id,
                    last_episode=str(current_ep),
                    progress=current_pos or "00:00:00",
                    is_secret=is_sec
                ), is_secret=is_sec)
            except Exception:
                pass

            exit_code, last_pos, elapsed = player.play(
                stream_url=stream_source.stream_url,
                media_title=media_title,
                start_pos=current_pos,
                referer=stream_source.referer
            )
            final_pos = last_pos

            # Si MPV falló en menos de 4 segundos con código de salida != 0, failover al siguiente servidor
            if exit_code != 0 and elapsed < 4:
                remaining = len(stream_sources) - idx - 1
                if remaining > 0:
                    print_warning(
                        f"El servidor '{stream_source.server_name}' falló al reproducir. Probando servidor alternativo ({remaining} restante(s))..."
                    )
                    continue
                else:
                    print_error(f"El servidor '{stream_source.server_name}' falló al reproducir.")
            else:
                playback_success = True
                break

        if not playback_success:
            print_error(f"No se pudo reproducir el capítulo {current_ep} con ninguno de los servidores encontrados.")
            action = fzf.select(
                [
                    "🔄 Reintentar este capítulo",
                    "📋 Cambiar capítulo",
                    "🔍 Buscar otro anime",
                    "❌ Salir"
                ],
                prompt="  ❯ ",
                header=f"{short_title} Error • ↑/↓/TAB: Elegir • ENTER: Aceptar • ESC: Volver"
            )
            if not action:
                return "BACK"
            elif "Salir" in action:
                print("¡Hasta la próxima!")
                return "EXIT"
            elif "Buscar otro anime" in action:
                return "SEARCH"
            elif "Reintentar" in action:
                continue
            elif "Cambiar capítulo" in action and episodes:
                anime_history = db.get_anime(anime_title)
                last_ep = str(current_ep) or (anime_history.last_episode if anime_history else None)
                episode_options = [ep.format_menu_line(current_watched_ep=last_ep) for ep in episodes]
                while True:
                    sel = fzf.select(
                        episode_options,
                        prompt="  ❯ ",
                        header=f"{short_title} • ↑/↓/TAB: Navegar • ENTER: Ver • ESC: Volver"
                    )
                    if not sel:
                        break
                    p = sel.split("\t")
                    if len(p) > 1 and p[1] == "HEADER":
                        continue
                    if len(p) > 2 and p[2].isdigit():
                        current_ep = int(p[2])
                        current_ep_url = p[1]
                        current_pos = "00:00:00"
                        break
                continue
            return "SEARCH"

        # Actualizar historial de forma segura con la posición final
        try:
            is_sec = bool(secret_mode or provider_id == "secret")
            db.save_progress(HistoryEntry(
                anime_title=anime_title,
                url=anime_url,
                provider=provider_id,
                last_episode=str(current_ep),
                progress=final_pos,
                is_secret=is_sec
            ), is_secret=is_sec)
        except Exception:
            pass

        # Opciones posteriores a la reproducción
        next_ep = current_ep + 1
        prev_ep = current_ep - 1
        actions = [f"▶ Siguiente (Capítulo {next_ep})"]
        if prev_ep >= 1:
            actions.append(f"◀ Anterior (Capítulo {prev_ep})")
        actions.extend([
            f"🔄 Repetir Capítulo {current_ep}",
            "📋 Cambiar capítulo",
            "🔍 Buscar otro anime",
            "❌ Salir"
        ])

        action = fzf.select(
            actions,
            prompt="  ❯ ",
            header=f"{short_title} Cap {current_ep} • ↑/↓/TAB: Elegir • ENTER: Aceptar • ESC: Volver"
        )
        if not action:
            # Presionó ESC -> volver a la lista de episodios / animes
            return "BACK"
        elif "Salir" in action:
            print("¡Hasta la próxima!")
            return "EXIT"
        elif "Buscar otro anime" in action:
            return "SEARCH"
        elif "Siguiente" in action:
            current_ep = next_ep
            current_pos = "00:00:00"
        elif "Anterior" in action:
            current_ep = prev_ep
            current_pos = "00:00:00"
        elif "Repetir" in action:
            current_pos = "00:00:00"
        elif "Cambiar capítulo" in action and episodes:
            anime_history = db.get_anime(anime_title)
            last_ep = str(current_ep) or (anime_history.last_episode if anime_history else None)
            episode_options = [ep.format_menu_line(current_watched_ep=last_ep) for ep in episodes]
            while True:
                sel = fzf.select(
                    episode_options,
                    prompt="  ❯ ",
                    header=f"{short_title} • ↑/↓/TAB: Navegar • ENTER: Ver • ESC: Volver"
                )
                if not sel:
                    break
                p = sel.split("\t")
                if len(p) > 1 and p[1] == "HEADER":
                    continue
                if len(p) > 2 and p[2].isdigit():
                    current_ep = int(p[2])
                    current_ep_url = p[1]
                    current_pos = "00:00:00"
                    break

if __name__ == "__main__":
    main()
