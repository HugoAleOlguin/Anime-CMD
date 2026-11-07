"""Controlador y lanzador para el reproductor MPV."""
import os
import re
import sys
import time
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Tuple
from src.core.config import MPV_LOG_PATH, DEFAULT_HEADERS

class MPVPlayer:
    def __init__(self):
        self.mpv_path = self._find_mpv()

    def _find_mpv(self) -> Optional[str]:
        # 1. PATH del sistema
        which = shutil.which("mpv")
        if which:
            return which

        # 2. Rutas comunes en Windows
        if sys.platform == "win32":
            home = Path.home()
            local_appdata = os.environ.get("LOCALAPPDATA", "")
            candidates = [
                Path(local_appdata) / "Programs" / "mpv" / "mpv.exe",
                Path(local_appdata) / "Microsoft" / "WinGet" / "Links" / "mpv.exe",
                Path("C:/Program Files/mpv/mpv.exe"),
                Path("C:/Program Files (x86)/mpv/mpv.exe"),
                home / "scoop" / "shims" / "mpv.exe",
                home / "scoop" / "apps" / "mpv" / "current" / "mpv.exe",
            ]
            for c in candidates:
                if c.exists():
                    return str(c)
        return None

    def play(
        self,
        stream_url: str,
        media_title: str,
        start_pos: str = "00:00:00",
        referer: Optional[str] = None
    ) -> Tuple[int, str, int]:
        """
        Ejecuta MPV para reproducir el stream.
        Retorna: (exit_code, last_timestamp, seconds_elapsed)
        """
        if not isinstance(stream_url, str) or not (stream_url.startswith("http://") or stream_url.startswith("https://")) or stream_url.startswith("-"):
            raise ValueError(f"URL de stream no permitida o insegura: {stream_url}")

        if not self.mpv_path:
            raise RuntimeError("mpv no fue encontrado en el sistema. Asegúrate de tener mpv instalado.")

        cmd = [
            self.mpv_path,
            "--cache=yes",
            "--demuxer-max-bytes=64M",
            "--demuxer-readahead-secs=30",
            "--hwdec=auto-safe",
            f"--start={start_pos}",
            "--msg-level=ffmpeg=no",
            f"--force-media-title={media_title}",
            f"--user-agent={DEFAULT_HEADERS['User-Agent']}"
        ]
        if referer:
            cmd.append(f"--referrer={referer}")

        # Delimitador estándar para prevenir CLI Option Injection
        cmd.append("--")
        cmd.append(stream_url)

        t_start = time.time()
        last_pos = start_pos
        exit_code = 0

        # Guardar log para capturar progreso de tiempo
        with open(MPV_LOG_PATH, "w", encoding="utf-8", errors="ignore") as log_file:
            try:
                proc = subprocess.run(
                    cmd,
                    stdout=log_file,
                    stderr=subprocess.STDOUT,
                    check=False
                )
                exit_code = proc.returncode
            except KeyboardInterrupt:
                exit_code = 0

        t_elapsed = int(time.time() - t_start)

        # Extraer última posición AV: HH:MM:SS
        if MPV_LOG_PATH.exists():
            try:
                content = MPV_LOG_PATH.read_text(encoding="utf-8", errors="ignore")
                matches = re.findall(r"AV:\s*(\d{2}:\d{2}:\d{2})", content)
                if matches:
                    last_pos = matches[-1]
            except Exception:
                pass

        return exit_code, last_pos, t_elapsed
