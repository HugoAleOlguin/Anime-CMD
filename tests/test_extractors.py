"""Pruebas unitarias para extractores de video."""
import unittest
import ssl
import urllib.error
from unittest.mock import patch, MagicMock
from src.extractors.registry import ExtractorRegistry
from src.extractors.streamwish import StreamwishExtractor
from src.extractors.streamtape import StreamtapeExtractor
from src.extractors.base import fetch_embed_html
from src.providers.base import BaseProvider
from src.core.models import StreamSource

class DummyProvider(BaseProvider):
    def search(self, query: str, force_sub: bool = False):
        return []
    def get_episodes(self, anime_url: str):
        return []
    def get_embed_urls(self, episode_url: str, pref_audio: str = "latino", episode_num=None):
        return []

class TestExtractors(unittest.TestCase):
    def test_registry_matching(self):
        reg = ExtractorRegistry()
        self.assertTrue(any(e.matches("https://streamtape.com/v/12345") for e in reg._extractors))
        self.assertTrue(any(e.matches("https://streamwish.to/e/abcdef") for e in reg._extractors))
        self.assertTrue(any(e.matches("https://www.mp4upload.com/embed-xyz.html") for e in reg._extractors))
        self.assertTrue(any(e.matches("https://www.yourupload.com/embed/98765") for e in reg._extractors))
        self.assertTrue(any(e.matches("https://voe.sx/e/54321") for e in reg._extractors))

    def test_streamwish_unpack(self):
        ext = StreamwishExtractor()
        # Packed js de prueba
        packed = "eval(function(p,a,c,k,e,d){return p}('0://1.2/3.4',5,5,'https|server|com|video|m3u8'.split('|')))"
        res = ext._unpack_packed_js(packed)
        self.assertEqual(res, "https://server.com/video.m3u8")

    def test_direct_stream_detection(self):
        reg = ExtractorRegistry()
        direct = reg.resolve("https://example.com/anime/capitulo1.mp4", check_stream=False)
        self.assertIsNotNone(direct)
        self.assertEqual(direct.stream_url, "https://example.com/anime/capitulo1.mp4")

    def test_mega_embed_not_resolved_as_generic(self):
        reg = ExtractorRegistry()
        # mega.nz embeds are not directly playable in MPV and should not return generic
        res = reg.resolve("https://mega.nz/embed/!nc5SVILa!9x8CsgM-6p8MOI0LyMpu6MnpDJyCXDRqp_Fr3Kojt3I")
        self.assertIsNone(res)

    def test_resolve_scheme_and_ntlm_validation(self):
        reg = ExtractorRegistry()
        invalid_urls = [
            None,
            "",
            "   ",
            "file:///etc/passwd",
            "file:///C:/Windows/win.ini",
            "smb://192.168.1.1/share/video.mp4",
            r"\\192.168.1.1\share\video.mp4",
            r"\\attacker.com\ntlm_leak",
            "ftp://ftp.example.com/video.mp4",
            "javascript:alert(1)",
            "data:text/html,<html>test</html>",
            "http://example.com/smb:share/test.mp4",
            "https://example.com/file:passwords.txt",
            r"http://example.com\something.mp4",
        ]
        for url in invalid_urls:
            with self.subTest(url=url):
                self.assertIsNone(reg.resolve(url, check_stream=False))

    def test_resolve_first_returns_first_and_shuts_down(self):
        reg = ExtractorRegistry()
        embeds = [
            {"url": "https://streamtape.com/v/fast1"},
            {"url": "https://streamtape.com/v/slow2"},
            {"url": "https://streamtape.com/v/slow3"},
        ]
        mock_source = StreamSource(server_name="streamtape", stream_url="https://streamtape.com/stream.mp4")

        with patch.object(reg, "resolve", return_value=mock_source):
            res = reg.resolve_first(embeds, max_candidates=3, max_workers=2)
            self.assertIsNotNone(res)
            self.assertEqual(res.stream_url, "https://streamtape.com/stream.mp4")

    def test_provider_ssl_resilient_fallback(self):
        prov = DummyProvider()
        mock_resp = MagicMock()
        mock_resp.read.return_value = b"<html>fallback content</html>"
        mock_resp.__enter__.return_value = mock_resp

        # Simular fallo SSL en la primera llamada, éxito en la segunda con contexto inseguro
        with patch("urllib.request.urlopen", side_effect=[ssl.SSLError("certificate verify failed"), mock_resp]) as mock_urlopen:
            html = prov.fetch_html("https://pirate-site.tv")
            self.assertEqual(html, "<html>fallback content</html>")
            self.assertEqual(mock_urlopen.call_count, 2)

    def test_provider_no_fallback_on_http_error(self):
        prov = DummyProvider()
        http_err = urllib.error.HTTPError("https://example.com", 404, "Not Found", {}, None)

        with patch("urllib.request.urlopen", side_effect=http_err) as mock_urlopen:
            html = prov.fetch_html("https://example.com/404")
            self.assertEqual(html, "")
            self.assertEqual(mock_urlopen.call_count, 1)

    def test_extractor_ssl_resilient_fallback(self):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b"<html>extractor fallback</html>"
        mock_resp.__enter__.return_value = mock_resp

        url_err = urllib.error.URLError(ssl.SSLError("handshake failed"))
        with patch("urllib.request.urlopen", side_effect=[url_err, mock_resp]) as mock_urlopen:
            html = fetch_embed_html("https://video-cdn.com/embed")
            self.assertEqual(html, "<html>extractor fallback</html>")
            self.assertEqual(mock_urlopen.call_count, 2)

if __name__ == "__main__":
    unittest.main()
