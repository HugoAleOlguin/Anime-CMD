"""Extractor para Mediafire."""
import re
from typing import Optional
from src.extractors.base import BaseExtractor, fetch_embed_html
from src.core.models import StreamSource

class MediafireExtractor(BaseExtractor):
    name = "Mediafire"

    def matches(self, url: str) -> bool:
        return "mediafire.com" in url.lower()

    def extract(self, url: str, referer: Optional[str] = None) -> Optional[StreamSource]:
        html = fetch_embed_html(url, referer=referer)
        if not html:
            return None

        m = re.search(r'href=["\'](https?://download[^\'"]+)["\']', html)
        if m:
            return StreamSource(server_name=self.name, stream_url=m.group(1), referer="https://www.mediafire.com/")

        m = re.search(r'aria-label=["\']Download file["\']\s+href=["\']([^"\']+)["\']', html)
        if m:
            return StreamSource(server_name=self.name, stream_url=m.group(1), referer="https://www.mediafire.com/")

        return None
