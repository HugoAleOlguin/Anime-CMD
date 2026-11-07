"""Extractor para Voex (voe.sx)."""
import re
from typing import Optional
from src.extractors.base import BaseExtractor, fetch_embed_html
from src.core.models import StreamSource

class VoeExtractor(BaseExtractor):
    name = "Voex"

    def matches(self, url: str) -> bool:
        u = url.lower()
        return "voe.sx" in u or "voe-" in u

    def extract(self, url: str, referer: Optional[str] = None) -> Optional[StreamSource]:
        html = fetch_embed_html(url, referer=referer)
        if not html:
            return None

        m = re.search(r'["\']hls["\']\s*:\s*["\'](https?://[^\'"]+)["\']', html)
        if m:
            return StreamSource(server_name=self.name, stream_url=m.group(1), referer="https://voe.sx/")

        m = re.search(r'["\']mp4["\']\s*:\s*["\'](https?://[^\'"]+)["\']', html)
        if m:
            return StreamSource(server_name=self.name, stream_url=m.group(1), referer="https://voe.sx/")

        return None
