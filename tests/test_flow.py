import unittest
import re
from unittest.mock import patch, MagicMock
from src.core.models import EpisodeItem, AudioType, AnimeResult, HistoryEntry
from src.providers.animeonline import AnimeOnlineProvider
from src.providers.tioanime import TioAnimeProvider
from src.providers.monoschinos import MonosChinosProvider
from src.providers.jkanime import JKAnimeProvider
from src.main import main

class TestFlowLogic(unittest.TestCase):
    def test_title_cleaning(self):
        cases = [
            ("🔊 [LAT] [Anime Online] Re:Zero kara Hajimeru Isekai Seikatsu", "Re:Zero kara Hajimeru Isekai Seikatsu"),
            ("🇯🇵 [SUB] [TioAnime] Tokyo Revengers", "Tokyo Revengers"),
            ("🇪🇸 [CAST] [MonosChinos] Bleach", "Bleach"),
            ("[JKAnime] Solo Leveling", "Solo Leveling"),
            ("Attack on Titan", "Attack on Titan"),
            # Nuevos formatos tabulares con Tokyo Night y separador vertical
            ("[LAT]  │ [AnimeOnline]   │ Tokyo Revengers", "Tokyo Revengers"),
            ("[SUB]  │ [MonosChinos]   │ Bleach Sennen Kessen", "Bleach Sennen Kessen"),
            ("[CAST] │ [JKAnime]       │ Dragon Ball Super", "Dragon Ball Super"),
        ]
        for raw, expected in cases:
            cleaned = re.sub(r"^(?:[^\w\s]*\s*\[[^\]]+\]\s*)+", "", raw).strip(" │\t")
            self.assertEqual(cleaned, expected)

    def test_episode_map_generation(self):
        episodes = [
            EpisodeItem(number="HEADER", title="Temporada 1", url="http://test.com", is_season_header=True),
            EpisodeItem(number="1", title="Episodio 1", url="http://test.com/ep-1"),
            EpisodeItem(number="2", title="Episodio 2", url="http://test.com/ep-2"),
            EpisodeItem(number="HEADER", title="Temporada 2", url="http://test.com", is_season_header=True),
            EpisodeItem(number="3", title="Episodio 3", url="http://test.com/ep-3"),
        ]
        ep_map = {int(e.number): e for e in episodes if not e.is_season_header and e.number.isdigit()}
        self.assertEqual(len(ep_map), 3)
        self.assertEqual(ep_map[1].url, "http://test.com/ep-1")
        self.assertEqual(ep_map[3].url, "http://test.com/ep-3")

    def test_providers_accept_episode_num(self):
        providers = [
            AnimeOnlineProvider(),
            TioAnimeProvider(),
            MonosChinosProvider(),
            JKAnimeProvider()
        ]
        for p in providers:
            import inspect
            sig = inspect.signature(p.get_embed_urls)
            self.assertIn("episode_num", sig.parameters)
            self.assertIn("pref_audio", sig.parameters)

    @patch("src.main.play_flow")
    @patch("src.core.db.DatabaseManager.get_last_watched")
    @patch("builtins.input", return_value="")
    def test_quick_resume_enter_triggers_play_flow(self, mock_input, mock_last_watched, mock_play):
        """Si no se pasa búsqueda y el usuario presiona ENTER, debe reanudar el último anime."""
        mock_last_watched.return_value = HistoryEntry(
            anime_title="Tokyo Revengers",
            url="https://animeonline.ninja/online/tokyo-revengers/",
            provider="animeonline",
            last_episode="57",
            progress="00:01:23"
        )
        with patch("sys.argv", ["anime"]):
            main()

        mock_play.assert_called_once()
        kwargs = mock_play.call_args.kwargs
        self.assertEqual(kwargs["anime_title"], "Tokyo Revengers")
        self.assertEqual(kwargs["episode_num"], "57")
        self.assertEqual(kwargs["start_pos"], "00:01:23")

    @patch("src.main.print_help")
    @patch("builtins.input", return_value="-c")
    def test_typing_c_in_prompt_shows_help(self, mock_input, mock_help):
        """Escribir '-c' en el prompt debe mostrar la ayuda y comandos."""
        with patch("sys.argv", ["anime"]):
            main()
        mock_help.assert_called_once()

    @patch("src.main.print_help")
    def test_flag_c_shows_help(self, mock_help):
        """El flag 'anime -c' debe mostrar la ayuda y comandos."""
        with patch("sys.argv", ["anime", "-c"]):
            main()
        mock_help.assert_called_once()

    def test_play_flow_navigation_signals(self):
        """Verifica que play_flow responda con las señales correctas ante ESC, Buscar y Salir."""
        from src.main import play_flow
        from src.core.models import StreamSource

        mock_db = MagicMock()
        mock_fzf = MagicMock()
        mock_ext = MagicMock()
        mock_player = MagicMock()

        # Simular stream resuelto y reproducción exitosa
        mock_ext.resolve_candidates.return_value = [
            StreamSource(server_name="TestServer", stream_url="https://test.com/v.mp4")
        ]
        mock_player.play.return_value = (0, "00:05:00", 120)

        mock_prov_reg = MagicMock()
        mock_prov = MagicMock()
        mock_prov.get_embed_urls.return_value = [{"url": "http://test"}]
        mock_prov_reg.get.return_value = mock_prov

        # 1. ESC en menú posterior -> Debe retornar "BACK"
        mock_fzf.select.return_value = None
        res_esc = play_flow(
            anime_title="Test Anime",
            anime_url="http://test.com/anime",
            provider_id="test",
            episode_num="1",
            start_pos="00:00:00",
            db=mock_db,
            fzf=mock_fzf,
            player=mock_player,
            provider_reg=mock_prov_reg,
            extractor_reg=mock_ext,
            force_sub=False
        )
        self.assertEqual(res_esc, "BACK")

        # 2. 'Buscar otro anime' -> Debe retornar "SEARCH"
        mock_fzf.select.return_value = "🔍 Buscar otro anime"
        res_search = play_flow(
            anime_title="Test Anime",
            anime_url="http://test.com/anime",
            provider_id="test",
            episode_num="1",
            start_pos="00:00:00",
            db=mock_db,
            fzf=mock_fzf,
            player=mock_player,
            provider_reg=mock_prov_reg,
            extractor_reg=mock_ext,
            force_sub=False
        )
        self.assertEqual(res_search, "SEARCH")

        # 3. 'Salir' -> Debe retornar "EXIT"
        mock_fzf.select.return_value = "❌ Salir"
        res_exit = play_flow(
            anime_title="Test Anime",
            anime_url="http://test.com/anime",
            provider_id="test",
            episode_num="1",
            start_pos="00:00:00",
            db=mock_db,
            fzf=mock_fzf,
            player=mock_player,
            provider_reg=mock_prov_reg,
            extractor_reg=mock_ext,
            force_sub=False
        )
        self.assertEqual(res_exit, "EXIT")

    @patch("src.main.FZFSelector")
    @patch("src.main.ProviderRegistry")
    @patch("builtins.input", side_effect=["naruto", "salir"])
    def test_anime_list_esc_returns_to_search_prompt(self, mock_input, mock_prov_reg_cls, mock_fzf_cls):
        """Al presionar ESC en la lista de resultados de anime, debe regresar al prompt de búsqueda."""
        from src.core.models import AnimeResult, AudioType
        mock_prov_reg = mock_prov_reg_cls.return_value
        mock_prov_reg.search_all.return_value = [
            AnimeResult(title="Naruto", url="http://test/naruto", provider_id="test", provider_name="Test", audio_type=AudioType.LATINO)
        ]
        # Primer select (lista de animes) retorna None (simulando ESC)
        mock_fzf = mock_fzf_cls.return_value
        mock_fzf.select.return_value = None

        with patch("sys.argv", ["anime"]):
            main()

        # Debe haber consultado el input 2 veces (la primera búsqueda con ESC y luego 'salir')
        self.assertEqual(mock_input.call_count, 2)

if __name__ == "__main__":
    unittest.main()
