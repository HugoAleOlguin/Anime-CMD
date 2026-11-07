"""Pruebas unitarias para la capa visual, temas y formato TUI."""
import unittest
import io
import sys
from unittest.mock import patch

from src.core.models import AnimeResult, AudioType, EpisodeItem, HistoryEntry

class TestUIComponents(unittest.TestCase):

    def test_theme_constants(self):
        """Verifica que el tema Tokyo Night y los argumentos de FZF estén definidos."""
        from src.ui import theme
        self.assertTrue(hasattr(theme, "CYAN"))
        self.assertTrue(hasattr(theme, "PURPLE"))
        self.assertTrue(hasattr(theme, "BLUE"))
        self.assertTrue(hasattr(theme, "ORANGE"))
        self.assertTrue(hasattr(theme, "GREEN"))
        self.assertTrue(hasattr(theme, "GRAY"))
        self.assertTrue(hasattr(theme, "WHITE"))
        self.assertTrue(hasattr(theme, "FZF_THEME_ARGS"))
        self.assertIn("--border=rounded", theme.FZF_THEME_ARGS)
        self.assertIn("--layout=reverse", theme.FZF_THEME_ARGS)
        self.assertIn("--cycle", theme.FZF_THEME_ARGS)
        self.assertIn("--highlight-line", theme.FZF_THEME_ARGS)
        self.assertIn("--pointer=▶ ", theme.FZF_THEME_ARGS)
        self.assertTrue(any(arg.startswith("--bind=") for arg in theme.FZF_THEME_ARGS))
        self.assertIn("--color=", [arg for arg in theme.FZF_THEME_ARGS if arg.startswith("--color=")][0])

    def test_anime_result_format_menu_line(self):
        """Verifica el formato tabular con badges de AnimeResult y título limpio en 4ta columna."""
        res = AnimeResult(
            title="Tokyo Revengers",
            url="https://animeonline.ninja/online/tokyo-revengers/",
            provider_id="animeonline",
            provider_name="AnimeOnline",
            audio_type=AudioType.LATINO
        )
        line = res.format_menu_line()
        parts = line.split("\t")
        self.assertEqual(len(parts), 4)
        display_part, url, prov_id, clean_title = parts
        self.assertIn("[LAT]", display_part)
        self.assertIn("AnimeOnline", display_part)
        self.assertIn("Tokyo Revengers", display_part)
        self.assertEqual(url, "https://animeonline.ninja/online/tokyo-revengers/")
        self.assertEqual(prov_id, "animeonline")
        self.assertEqual(clean_title, "Tokyo Revengers")

    def test_episode_item_format_menu_line(self):
        """Verifica el formato de capítulos con títulos reales, separadores llamativos y badge de visto."""
        header = EpisodeItem(
            number="0",
            title="Temporada 2",
            url="",
            is_season_header=True
        )
        header_line = header.format_menu_line()
        self.assertIn("HEADER", header_line)
        self.assertIn("TEMPORADA 2", header_line)
        self.assertIn("🌸", header_line)

        ep = EpisodeItem(
            number="57",
            title="Renacer y Resistir",
            url="https://animeonline.ninja/episodio/57"
        )
        # Probando sin ser el visto
        ep_line = ep.format_menu_line()
        parts = ep_line.split("\t")
        self.assertEqual(len(parts), 4)
        self.assertIn("Cap. 57", parts[0])
        self.assertIn("Renacer y Resistir", parts[0])
        self.assertEqual(parts[1], "https://animeonline.ninja/episodio/57")
        self.assertEqual(parts[2], "57")
        self.assertEqual(parts[3], "Renacer y Resistir")

        # Probando con current_watched_ep="57"
        watched_line = ep.format_menu_line(current_watched_ep="57")
        self.assertIn("★ [Último Visto]", watched_line)

        # Probando con badge de temporada [T2]
        ep_season = EpisodeItem(
            number="45",
            title="Episodio 14",
            url="https://animeonline.ninja/episodio/45",
            season="Temporada 2"
        )
        line_season = ep_season.format_menu_line()
        self.assertIn("[T2]", line_season)

    def test_print_quick_resume(self):
        """Verifica la tarjeta interactiva de reanudación rápida."""
        from src.ui.printer import print_quick_resume
        entry = HistoryEntry(
            anime_title="Tokyo Revengers",
            url="https://animeonline.ninja/online/tokyo-revengers/",
            provider="animeonline",
            last_episode="57",
            progress="00:01:23"
        )
        captured = io.StringIO()
        with patch("sys.stdout", captured):
            print_quick_resume(entry)

        output = captured.getvalue()
        self.assertIn("ANIME-CMD", output)
        self.assertIn("Reproductor de anime", output)
        self.assertIn("Tokyo Revengers", output)
        self.assertIn("57", output)
        self.assertIn("00:01:23", output)
        self.assertIn("╭", output)
        self.assertIn("╰", output)

    def test_clear_screen(self):
        """Verifica que clear_screen invoque el comando adecuado según el SO."""
        from src.ui.printer import clear_screen
        with patch("os.system") as mock_os_system:
            clear_screen()
            mock_os_system.assert_called_once()

    def test_fzf_command_generation(self):
        """Verifica que FZFSelector arme el comando con los argumentos modernos."""
        from src.ui.fzf import FZFSelector
        selector = FZFSelector()
        selector.fzf_path = "fzf.exe"
        cmd = selector.build_cmd(prompt="  ❯ ", height="40%")
        self.assertIn("--border=rounded", cmd)
        self.assertIn("--layout=reverse", cmd)
        self.assertIn("--prompt=  ❯ ", cmd)

if __name__ == "__main__":
    unittest.main()
