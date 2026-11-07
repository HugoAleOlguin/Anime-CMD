"""Clase base y utilidades para extractores de video."""
import re
import ssl
import urllib.request
import urllib.error
from abc import ABC, abstractmethod
from typing import Optional
from src.core.models import StreamSource
from src.core.config import DEFAULT_HEADERS

try:
    import certifi
    cafile = certifi.where()
except ImportError:
    cafile = None

_default_ssl_context = ssl.create_default_context(cafile=cafile) if cafile else ssl.create_default_context()

_insecure_ssl_context = ssl.create_default_context()
_insecure_ssl_context.check_hostname = False
_insecure_ssl_context.verify_mode = ssl.CERT_NONE

# Mantener referencia ctx para compatibilidad
ctx = _insecure_ssl_context


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


def fetch_embed_html(url: str, timeout: int = 4, referer: Optional[str] = None) -> Optional[str]:
    """Obtiene el HTML del servidor de video con referer adecuado y fallback SSL resiliente."""
    headers = dict(DEFAULT_HEADERS)
    if referer:
        headers["Referer"] = referer
    try:
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=timeout, context=_default_ssl_context) as resp:
                return resp.read().decode("utf-8", errors="ignore")
        except Exception as e:
            if _is_ssl_error(e):
                with urllib.request.urlopen(req, timeout=timeout, context=_insecure_ssl_context) as resp:
                    return resp.read().decode("utf-8", errors="ignore")
            return None
    except Exception:
        return None

def verify_stream(url: str, referer: Optional[str] = None, timeout: float = 1.8) -> bool:
    """Verifica si el enlace de video responde con status 200/206 y no es un señuelo HTML."""
    if not url or not url.startswith("http"):
        return False
    try:
        headers = {
            "User-Agent": DEFAULT_HEADERS["User-Agent"],
            "Referer": referer or ""
        }
        if ".m3u8" not in url.lower():
            headers["Range"] = "bytes=0-1024"

        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            ctype = resp.headers.get("Content-Type", "").lower()
            if "text/html" in ctype:
                return False
            return resp.status in (200, 206)
    except urllib.error.HTTPError as e:
        if e.code in (401, 403, 404, 410):
            return False
        return True
    except Exception:
        return False

class BaseExtractor(ABC):
    name: str = "Base"

    @abstractmethod
    def matches(self, url: str) -> bool:
        pass

    @abstractmethod
    def extract(self, url: str, referer: Optional[str] = None) -> Optional[StreamSource]:
        pass
