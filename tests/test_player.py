"""Pruebas unitarias para el controlador de reproductor MPV (src/core/player.py)."""
import unittest
from unittest.mock import patch, MagicMock
from src.core.player import MPVPlayer


class TestMPVPlayerSecurity(unittest.TestCase):
    def setUp(self):
        self.player = MPVPlayer()
        # Aseguramos que mpv_path tenga un valor simulado para pruebas de comando
        self.player.mpv_path = "mpv"

    @patch("subprocess.run")
    def test_malicious_cli_flag_injection_rejected(self, mock_subprocess):
        """Verifica que URLs que comiencen con banderas CLI como --script= sean rechazadas con ValueError."""
        malicious_urls = [
            "--script=/tmp/bad.lua",
            "--o=pwn.exe",
            "--config=/etc/shadow",
            "-v",
            "--input-ipc-server=/tmp/sock",
        ]
        for bad_url in malicious_urls:
            with self.subTest(bad_url=bad_url):
                with self.assertRaises(ValueError) as ctx:
                    self.player.play(stream_url=bad_url, media_title="Evil Title")
                self.assertIn("URL de stream no permitida o insegura", str(ctx.exception))
                mock_subprocess.assert_not_called()

    @patch("subprocess.run")
    def test_dangerous_schemes_rejected(self, mock_subprocess):
        """Verifica que esquemas no HTTP/HTTPS sean rechazados inmediatamente."""
        dangerous_urls = [
            "file:///etc/passwd",
            "file://C:/Windows/win.ini",
            "smb://malicious.host/payload.exe",
            "ftp://files.example.com/stream.mp4",
            "javascript:alert(1)",
            "data:text/html;base64,PHNjcmlwdD4=",
            "",
            None,
        ]
        for url in dangerous_urls:
            with self.subTest(url=url):
                with self.assertRaises(ValueError):
                    self.player.play(stream_url=url, media_title="Test Title")
                mock_subprocess.assert_not_called()

    @patch("subprocess.run")
    @patch("src.core.player.open")
    def test_legitimate_url_includes_end_of_options_delimiter(self, mock_open, mock_subprocess):
        """Verifica que una URL legítima inserte '--' inmediatamente antes de stream_url."""
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_subprocess.return_value = mock_proc

        stream_url = "https://stream.server.com/video.m3u8"
        title = "Episodio 1"
        self.player.play(
            stream_url=stream_url,
            media_title=title,
            start_pos="00:01:30",
            referer="https://anime-site.com"
        )

        mock_subprocess.assert_called_once()
        cmd = mock_subprocess.call_args[0][0]

        # Verificar que '--' está en la lista de argumentos
        self.assertIn("--", cmd)
        # Verificar que '--' precede directamente a stream_url
        dash_dash_idx = cmd.index("--")
        self.assertEqual(cmd[dash_dash_idx + 1], stream_url)
        # Verificar que el último elemento es el stream_url
        self.assertEqual(cmd[-1], stream_url)
        self.assertEqual(cmd[-2], "--")

        # Verificar banderas esenciales
        self.assertIn("--referrer=https://anime-site.com", cmd)
        self.assertIn("--start=00:01:30", cmd)
        self.assertIn(f"--force-media-title={title}", cmd)

    @patch("subprocess.run")
    @patch("src.core.player.open")
    def test_http_url_allowed_with_proper_delimiter(self, mock_open, mock_subprocess):
        """Verifica que URLs legítimas http:// también sean permitidas y delimitadas."""
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_subprocess.return_value = mock_proc

        stream_url = "http://plain.server.org/live.mp4"
        self.player.play(stream_url=stream_url, media_title="Live Stream")

        cmd = mock_subprocess.call_args[0][0]
        self.assertEqual(cmd[-2], "--")
        self.assertEqual(cmd[-1], stream_url)

    def test_missing_mpv_binary_raises_runtime_error(self):
        """Verifica que si mpv no existe en el sistema y la URL es válida, se lance RuntimeError."""
        self.player.mpv_path = None
        with self.assertRaises(RuntimeError) as ctx:
            self.player.play("https://stream.example.com/video.m3u8", "Title")
        self.assertIn("mpv no fue encontrado", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
