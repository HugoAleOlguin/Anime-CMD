"""Modelos de datos fuertemente tipados para Anime-CMD con soporte TrueColor ANSI."""
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict
from src.ui.theme import (
    GREEN, BLUE, ORANGE, PURPLE, CYAN, GRAY, WHITE, BOLD, RESET, PROVIDER_COLORS
)

class AudioType(Enum):
    LATINO = "[LAT]"
    CASTELLANO = "[CAST]"
    SUBTITULADO = "[SUB]"

    @classmethod
    def from_text(cls, text: str) -> "AudioType":
        t = text.lower()
        if "latino" in t or "audio latino" in t:
            return cls.LATINO
        if "castellano" in t:
            return cls.CASTELLANO
        return cls.SUBTITULADO

@dataclass
class AnimeResult:
    title: str
    url: str
    provider_id: str
    provider_name: str
    audio_type: AudioType
    description: Optional[str] = None

    def display_tag(self) -> str:
        return self.audio_type.value

    def format_menu_line(self) -> str:
        """Formatea la línea con columnas coloreadas y envía el título limpio en la 4ta columna."""
        if self.audio_type == AudioType.LATINO:
            tag_str = f"{GREEN}[LAT] {RESET}"
        elif self.audio_type == AudioType.CASTELLANO:
            tag_str = f"{BLUE}[CAST]{RESET}"
        else:
            tag_str = f"{ORANGE}[SUB] {RESET}"

        color = PROVIDER_COLORS.get(self.provider_id, WHITE)
        prov_label = f"● {self.provider_name}"
        prov_str = f"{color}{prov_label:<16}{RESET}"
        title_str = f"{BOLD}{WHITE}{self.title}{RESET}"

        display_part = f"{tag_str}  {GRAY}│{RESET}  {prov_str}  {GRAY}│{RESET}  {title_str}"
        return f"{display_part}\t{self.url}\t{self.provider_id}\t{self.title}"

@dataclass
class EpisodeItem:
    number: str
    title: str
    url: str
    season: Optional[str] = None
    is_season_header: bool = False

    def format_menu_line(self, current_watched_ep: Optional[str] = None) -> str:
        """Formatea la línea del episodio con números alineados, títulos limpios y separadores llamativos."""
        if self.is_season_header:
            s_name = self.title.upper()
            dash_count = max(10, 52 - len(s_name))
            return f"{PURPLE}{BOLD}🌸 ═══ [ {s_name} ] {'═' * dash_count}{RESET}\tHEADER\tHEADER"

        if self.number.isdigit() and int(self.number) < 100:
            num_padded = f"{int(self.number):02d}"
        else:
            num_padded = self.number

        raw_title = (self.title or "").strip()
        # Evitar duplicaciones como 'Capítulo 1: Episodio 1'
        if not raw_title or raw_title.lower() in (
            f"episodio {self.number}".lower(),
            f"capitulo {self.number}".lower(),
            f"capítulo {self.number}".lower()
        ):
            disp_title = f"Capítulo {self.number}"
        else:
            disp_title = raw_title

        # Badge de temporada compacto (ej: [T1], [T2], [PELI], etc.)
        season_badge = ""
        if self.season:
            s_clean = self.season.strip()
            m = re.search(r"(\d+)", s_clean)
            if m:
                season_badge = f"{PURPLE}[T{m.group(1)}]{RESET} "
            elif "pelicula" in s_clean.lower() or "película" in s_clean.lower():
                season_badge = f"{BLUE}[PELI]{RESET} "
            elif "ova" in s_clean.lower():
                season_badge = f"{ORANGE}[OVA]{RESET} "
            elif "especial" in s_clean.lower():
                season_badge = f"{CYAN}[ESP]{RESET} "

        watched_badge = f"  {GREEN}{BOLD}★ [Último Visto]{RESET}" if (current_watched_ep and str(current_watched_ep) == str(self.number)) else ""
        display_part = f"  {CYAN}▶{RESET} {season_badge}{BOLD}{WHITE}Cap. {num_padded}{RESET}  {GRAY}│{RESET}  {WHITE}{disp_title}{RESET}{watched_badge}"
        return f"{display_part}\t{self.url}\t{self.number}\t{disp_title}"

@dataclass
class StreamSource:
    server_name: str
    stream_url: str
    referer: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)

@dataclass
class HistoryEntry:
    anime_title: str
    url: str
    provider: str
    last_episode: str
    progress: str = "00:00:00"
    servers_data: Optional[str] = None
