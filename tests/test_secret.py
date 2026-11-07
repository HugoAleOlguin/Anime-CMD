"""Pruebas unitarias para el proveedor discreto SecretProvider (-hh)."""
import unittest
from unittest.mock import patch
from src.core.models import AudioType
from src.providers.secret import SecretProvider
from src.providers.registry import ProviderRegistry

class TestSecretProvider(unittest.TestCase):
    def setUp(self):
        self.provider = SecretProvider()

    def test_provider_metadata(self):
        self.assertEqual(self.provider.provider_id, "secret")
        self.assertEqual(self.provider.name, "Secret")
        self.assertIn("tiohentai", self.provider.base_url)

    def test_search_isolation_in_registry(self):
        """Verifica que el proveedor secret NO aparezca en búsquedas normales."""
        reg = ProviderRegistry()
        normal_provs = [p.provider_id for p in reg.list_providers()]
        self.assertNotIn("secret", normal_provs)

    def test_search_secret_mode(self):
        """Verifica que el registry solo invoque a secret cuando secret_mode=True."""
        reg = ProviderRegistry()
        # Mock search of secret provider
        class MockSecret:
            provider_id = "secret"
            name = "Secret"
            def search(self, query, force_sub=False):
                return ["mock_secret_result"]

        reg.secret_provider = MockSecret()
        # Modo normal -> lista normal
        res_normal = reg.search_all("overflow", secret_mode=False)
        self.assertNotIn("mock_secret_result", res_normal)

        # Modo secreto (-hh) -> lista de secret
        res_secret = reg.search_all("overflow", secret_mode=True)
        self.assertIn("mock_secret_result", res_secret)

    def test_parse_episodes(self):
        """Verifica la extracción de capítulos desde un fragmento de HTML de TioHentai."""
        sample_html = '''
        <html>
        <script>
        var episodes = [3, 2, 1];
        </script>
        </html>
        '''
        eps = self.provider._parse_episodes_from_html("https://tiohentai.com/hentai/test-anime", sample_html)
        self.assertEqual(len(eps), 3)
        self.assertEqual(eps[0].number, "1")
        self.assertEqual(eps[1].number, "2")
        self.assertEqual(eps[2].number, "3")

    def test_parse_videos(self):
        """Verifica la extracción de embeds de video."""
        sample_html = '''
        <script>
        var videos = [
            ["YourUpload", "https://www.yourupload.com/embed/12345", 0],
            ["Voe", "https://voe.sx/e/67890", 0]
        ];
        </script>
        '''
        embeds = self.provider._parse_videos_from_html(sample_html)
        self.assertEqual(len(embeds), 2)
        self.assertEqual(embeds[0]["url"], "https://www.yourupload.com/embed/12345")
        self.assertEqual(embeds[1]["url"], "https://voe.sx/e/67890")
        self.assertEqual(embeds[0]["referer"], "https://tiohentai.com/")

    def test_secret_database_privacy_isolation(self):
        """Verifica que el historial de animes secretos nunca sea expuesto en el modo normal."""
        import tempfile
        from pathlib import Path
        from src.core.db import DatabaseManager
        from src.core.models import HistoryEntry

        with tempfile.TemporaryDirectory() as tmpdir:
            db_file = Path(tmpdir) / "test_secret_privacy.db"
            db = DatabaseManager(db_path=db_file)

            # 1. Guardar contenido secreto
            secret_entry = HistoryEntry(
                anime_title="Overflow (Uncensored)",
                url="https://tiohentai.com/hentai/overflow",
                provider="secret",
                last_episode="8",
                progress="00:11:20"
            )
            db.save_progress(secret_entry)

            # Modo normal (sin -hh) -> NUNCA debe devolver el anime secreto
            normal_view = db.get_last_watched(include_secret=False)
            self.assertIsNone(normal_view)

            # Modo secreto (-hh) -> Sí debe devolverlo
            secret_view = db.get_last_watched(include_secret=True)
            self.assertIsNotNone(secret_view)
            self.assertEqual(secret_view.anime_title, "Overflow (Uncensored)")
            self.assertEqual(secret_view.provider, "secret")
            self.assertTrue(getattr(secret_view, "is_secret", False))

            # 2. Guardar un anime normal después del secreto
            normal_entry = HistoryEntry(
                anime_title="Demon Slayer",
                url="https://animeonline.ninja/online/kimetsu-no-yaiba/",
                provider="animeonline",
                last_episode="1"
            )
            db.save_progress(normal_entry)

            # Modo normal debe ver Demon Slayer
            self.assertEqual(db.get_last_watched(include_secret=False).anime_title, "Demon Slayer")

            # 3. Guardar otro anime secreto con flag is_secret=True
            secret_entry_2 = HistoryEntry(
                anime_title="Another Secret Title",
                url="https://tiohentai.com/hentai/another",
                provider="secret",
                last_episode="2"
            )
            db.save_progress(secret_entry_2, is_secret=True)

            # Modo normal DEBE seguir viendo 'Demon Slayer', protegiendo la privacidad
            self.assertEqual(db.get_last_watched(include_secret=False).anime_title, "Demon Slayer")

            # Modo secreto debe ver 'Another Secret Title'
            self.assertEqual(db.get_last_watched(include_secret=True).anime_title, "Another Secret Title")

    @patch("src.main.print_unified_card")
    @patch("src.core.db.DatabaseManager.get_last_watched")
    @patch("builtins.input", return_value="exit")
    def test_main_card_privacy_isolation(self, mock_input, mock_last_watched, mock_card):
        """Verifica que main() pase include_secret=False en modo normal y include_secret=True en modo -hh."""
        from src.main import main

        # Caso 1: Modo normal
        with patch("sys.argv", ["anime"]):
            main()
        mock_last_watched.assert_called_with(include_secret=False)

        mock_last_watched.reset_mock()

        # Caso 2: Modo secreto -hh
        with patch("sys.argv", ["anime", "-hh"]):
            main()
        mock_last_watched.assert_called_with(include_secret=True)

if __name__ == "__main__":
    unittest.main()
