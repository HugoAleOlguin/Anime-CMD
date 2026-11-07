"""Extractor para YourUpload."""
import re
from typing import Optional
from src.extractors.base import BaseExtractor, fetch_embed_html
from src.core.models import StreamSource

class YourUploadExtractor(BaseExtractor):
    name = "YourUpload"

    def matches(self, url: str) -> bool:
        return "yourupload.com" in url.lower()

    def extract(self, url: str, referer: Optional[str] = None) -> Optional[StreamSource]:
        html = fetch_embed_html(url, referer=referer)
        if not html:
            return None

        m = re.search(r'file:\s*["\'](https?://[^\'"]+\.mp4[^\'"]*)["\']', html)
        if m:
            return StreamSource(server_name=self.name, stream_url=m.group(1), referer="https://www.yourupload.com/")

        m = re.search(r'data-url=["\']([^"\']+\.mp4[^"\']*)["\']', html)
        if m:
            return StreamSource(server_name=self.name, stream_url=m.group(1), referer="https://www.yourupload.com/")

        return None
