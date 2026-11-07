"""Extractor para Mp4upload."""
import re
from typing import Optional
from src.extractors.base import BaseExtractor, fetch_embed_html
from src.core.models import StreamSource

class Mp4uploadExtractor(BaseExtractor):
    name = "Mp4upload"

    def matches(self, url: str) -> bool:
        return "mp4upload.com" in url.lower()

    def extract(self, url: str, referer: Optional[str] = None) -> Optional[StreamSource]:
        html = fetch_embed_html(url, referer=referer)
        if not html:
            return None

        m = re.search(r'player\.src\(\s*\{\s*type:\s*["\']video/mp4["\'],\s*src:\s*["\'](https?://[^\'"]+)["\']', html)
        if m:
            return StreamSource(server_name=self.name, stream_url=m.group(1), referer="https://www.mp4upload.com/")

        m = re.search(r'src:\s*["\'](https?://[^\'"]+\.mp4[^\'"]*)["\']', html)
        if m:
            return StreamSource(server_name=self.name, stream_url=m.group(1), referer="https://www.mp4upload.com/")

        return None
