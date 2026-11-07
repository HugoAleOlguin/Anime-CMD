"""Pruebas para proveedores y registro de búsqueda."""
import unittest
from src.core.models import AudioType, AnimeResult
from src.providers.registry import ProviderRegistry

class TestProviders(unittest.TestCase):
    def test_provider_registry_init(self):
        reg = ProviderRegistry()
        self.assertIsNotNone(reg.get("animeonline"))
        self.assertIsNotNone(reg.get("tioanime"))
        self.assertIsNotNone(reg.get("monoschinos"))
        self.assertIsNotNone(reg.get("jkanime"))
        self.assertIsNone(reg.get("inexistente"))

    def test_audio_type_detection(self):
        self.assertEqual(AudioType.from_text("Dragon Ball Z Audio Latino"), AudioType.LATINO)
        self.assertEqual(AudioType.from_text("Naruto Castellano"), AudioType.CASTELLANO)
        self.assertEqual(AudioType.from_text("One Piece Subtitulado"), AudioType.SUBTITULADO)

    def test_anime_result_format(self):
        item = AnimeResult(
            title="Naruto",
            url="https://tioanime.com/anime/naruto",
            provider_id="tioanime",
            provider_name="TioAnime",
            audio_type=AudioType.LATINO
        )
        line = item.format_menu_line()
        self.assertIn("[LAT]", line)
        self.assertIn("TioAnime", line)
        self.assertIn("https://tioanime.com/anime/naruto", line)

if __name__ == "__main__":
    unittest.main()
