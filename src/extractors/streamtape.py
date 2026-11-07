"""Extractor para Streamtape."""
import re
from typing import Optional
from src.extractors.base import BaseExtractor, fetch_embed_html
from src.core.models import StreamSource

class StreamtapeExtractor(BaseExtractor):
    name = "Streamtape"

    def matches(self, url: str) -> bool:
        return "streamtape" in url.lower()

    def extract(self, url: str, referer: Optional[str] = None) -> Optional[StreamSource]:
        html = fetch_embed_html(url, referer=referer)
        if not html:
            return None

        for target_id in ["robotlink", "botlink"]:
            pattern = (
                r"document\.getElementById\(['\"]" + target_id +
                r"['\"]\)\.innerHTML\s*=\s*['\"]([^'\"]+)['\"]\s*\+\s*\(['\"]([^'\"]+)['\"]\)\.substring\((\d+)\)(?:\.substring\((\d+)\))?"
            )
            m = re.search(pattern, html)
            if m:
                try:
                    base = m.group(1)
                    token_str = m.group(2)
                    s1 = int(m.group(3))
                    s2 = int(m.group(4)) if m.group(4) else 0
                    token_clean = token_str[s1:][s2:]
                    full = base + token_clean
                    if full.startswith("//"):
                        full = "https:" + full
                    full = re.sub(r"streamtape\.[a-z0-9]+", "streamtape.com", full)
                    if "&stream=1" not in full:
                        full += "&stream=1"
                    return StreamSource(
                        server_name=self.name,
                        stream_url=full,
                        referer="https://streamtape.com/"
                    )
                except Exception:
                    pass
        return None
