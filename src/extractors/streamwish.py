"""Extractor para Streamwish y clones (swdyu, sfastwish, etc.)."""
import re
from typing import Optional
from src.extractors.base import BaseExtractor, fetch_embed_html
from src.core.models import StreamSource

class StreamwishExtractor(BaseExtractor):
    name = "Streamwish"

    def matches(self, url: str) -> bool:
        u = url.lower()
        return any(k in u for k in ["streamwish", "swdyu", "sfastwish", "wishfast", "wishembed", "strwish"])

    def _unpack_packed_js(self, html: str) -> Optional[str]:
        m = re.search(
            r"eval\(function\(p,a,c,k,e,d\)\{.*?return p\}\('(.*?)',(\d+),(\d+),'([^']+)'\.split\('\|'\)",
            html,
            re.DOTALL
        )
        if not m:
            return None
        try:
            p, a, c, k = m.group(1), int(m.group(2)), int(m.group(3)), m.group(4).split("|")
            def base_n(num, b):
                digits = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
                res = ""
                while num:
                    res = digits[num % b] + res
                    num //= b
                return res or "0"

            for i in range(c - 1, -1, -1):
                if i < len(k) and k[i]:
                    p = re.sub(r"\b" + base_n(i, a) + r"\b", k[i], p)
            m3u8 = re.search(r"https?://[^\s\"']+\.m3u8[^\s\"']*", p)
            return m3u8.group(0) if m3u8 else None
        except Exception:
            return None

    def extract(self, url: str, referer: Optional[str] = None) -> Optional[StreamSource]:
        html = fetch_embed_html(url, referer=referer)
        if not html:
            return None

        # 1. Desempaquetar código JS ofuscado
        m3u8 = self._unpack_packed_js(html)
        if m3u8:
            return StreamSource(server_name=self.name, stream_url=m3u8, referer=url)

        # 2. Buscar directamente en fuentes
        m = re.search(r'file:\s*["\'](https?://[^\'"]+\.m3u8[^\'"]*)["\']', html)
        if m:
            return StreamSource(server_name=self.name, stream_url=m.group(1), referer=url)

        m = re.search(r'sources:\s*\[\{\s*file:\s*["\'](https?://[^\'"]+)["\']', html)
        if m:
            return StreamSource(server_name=self.name, stream_url=m.group(1), referer=url)

        return None
