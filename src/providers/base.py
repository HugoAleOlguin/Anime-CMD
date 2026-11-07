"""Clase base abstracta para proveedores de anime."""
import ssl
import urllib.request
import urllib.parse
import urllib.error
from abc import ABC, abstractmethod
from typing import List, Optional
from src.core.config import DEFAULT_HEADERS
from src.core.models import AnimeResult, EpisodeItem, StreamSource

try:
    import certifi
    cafile = certifi.where()
except ImportError:
    cafile = None

_insecure_ssl_context = ssl.create_default_context()
_insecure_ssl_context.check_hostname = False
_insecure_ssl_context.verify_mode = ssl.CERT_NONE


def _is_ssl_error(exc: Exception) -> bool:
    """Detecta si una excepción es un error SSL o URLError con causa SSL."""
    if isinstance(exc, ssl.SSLError):
        return True
    if isinstance(exc, urllib.error.URLError) and not isinstance(exc, urllib.error.HTTPError):
        reason = getattr(exc, "reason", None)
        if isinstance(reason, ssl.SSLError):
            return True
        reason_str = str(reason).lower()
        if any(term in reason_str for term in ("ssl", "certificate", "handshake", "cert")):
            return True
    return False


class BaseProvider(ABC):
    name: str = "Base"
    provider_id: str = "base"
    base_url: str = ""

    def __init__(self):
        self.ssl_context = ssl.create_default_context(cafile=cafile) if cafile else ssl.create_default_context()
        self._insecure_ssl_context = _insecure_ssl_context

    def fetch_html(self, url: str, timeout: int = 7, referer: Optional[str] = None) -> str:
        """Realiza una petición HTTP GET segura y retorna el HTML como string con fallback SSL resiliente."""
        headers = dict(DEFAULT_HEADERS)
        if referer:
            headers["Referer"] = referer
        try:
            req = urllib.request.Request(url, headers=headers)
            try:
                with urllib.request.urlopen(req, timeout=timeout, context=self.ssl_context) as resp:
                    return resp.read().decode("utf-8", errors="ignore")
            except Exception as e:
                if _is_ssl_error(e):
                    with urllib.request.urlopen(req, timeout=timeout, context=self._insecure_ssl_context) as resp:
                        return resp.read().decode("utf-8", errors="ignore")
                return ""
        except Exception:
            return ""

    @abstractmethod
    def search(self, query: str, force_sub: bool = False) -> List[AnimeResult]:
        """Busca animes que coincidan con la consulta."""
        pass

    @abstractmethod
    def get_episodes(self, anime_url: str) -> List[EpisodeItem]:
        """Obtiene la lista de capítulos del anime."""
        pass

    @abstractmethod
    def get_embed_urls(self, episode_url: str, pref_audio: str = "latino", episode_num: Optional[int] = None) -> List[dict]:
        """Extrae la lista de embeds de servidores del capítulo."""
        pass
