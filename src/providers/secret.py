"""Proveedor discreto para búsquedas y reproducción alternativa (-hh)."""
import re
import json
import urllib.parse
from typing import List, Optional, Dict
from bs4 import BeautifulSoup
from src.core.models import AnimeResult, EpisodeItem, AudioType
from src.providers.base import BaseProvider

try:
    from curl_cffi import requests as cffi_requests
except ImportError:
    cffi_requests = None

class SecretProvider(BaseProvider):
    name: str = "Secret"
    provider_id: str = "secret"
    base_url: str = "https://tiohentai.com"

    def _fetch(self, url: str) -> str:
        if cffi_requests:
            try:
                resp = cffi_requests.get(url, impersonate="chrome124", timeout=10)
                if resp.status_code == 200:
                    return resp.text
            except Exception:
                pass
        return self.fetch_html(url, referer=f"{self.base_url}/")

    def search(self, query: str, force_sub: bool = False) -> List[AnimeResult]:
        """Busca títulos en el catálogo alternativo."""
        q_url = f"{self.base_url}/directorio?q={urllib.parse.quote(query)}"
        html = self._fetch(q_url)
        if not html:
            return []

        results = []
        soup = BeautifulSoup(html, "html.parser")
        for item in soup.select(".anime article, article.anime, li.anime, article"):
            a = item.find("a", href=True)
            title_el = item.find(["h3", "h2", "span", "h4"])
            if a and title_el and "/hentai/" in a["href"]:
                title = title_el.get_text(strip=True)
                href = a["href"]
                if not href.startswith("http"):
                    href = f"{self.base_url}{href}"
                results.append(
                    AnimeResult(
                        title=title,
                        url=href,
                        provider_id=self.provider_id,
                        provider_name=self.name,
                        audio_type=AudioType.SUBTITULADO
                    )
                )

        # Fallback por regex si el parser de clases no capturó
        if not results:
            for m in re.finditer(r'<a\s+href="(/hentai/[^"]+)"[^>]*>.*?<h3[^>]*>([^<]+)</h3>', html, re.DOTALL):
                href = f"{self.base_url}{m.group(1)}"
                title = m.group(2).strip()
                results.append(
                    AnimeResult(
                        title=title,
                        url=href,
                        provider_id=self.provider_id,
                        provider_name=self.name,
                        audio_type=AudioType.SUBTITULADO
                    )
                )

        return results

    def _parse_episodes_from_html(self, anime_url: str, html: str) -> List[EpisodeItem]:
        slug = anime_url.rstrip("/").split("/")[-1]
        m = re.search(r'var episodes = (\[.*?\]);', html, re.DOTALL)
        if m:
            try:
                raw_eps = json.loads(m.group(1))
                if isinstance(raw_eps, list):
                    # Ordenar episodios numéricamente ascendente
                    sorted_eps = sorted([int(e) for e in raw_eps if str(e).isdigit()])
                    return [
                        EpisodeItem(
                            number=str(num),
                            title=f"Capítulo {num}",
                            url=f"{self.base_url}/ver/{slug}-{num}"
                        )
                        for num in sorted_eps
                    ]
            except Exception:
                pass

        # Fallback a episodio 1 único si no se pudo parsear array
        return [
            EpisodeItem(
                number="1",
                title="Capítulo 1",
                url=f"{self.base_url}/ver/{slug}-1"
            )
        ]

    def get_episodes(self, anime_url: str) -> List[EpisodeItem]:
        html = self._fetch(anime_url)
        if not html:
            slug = anime_url.rstrip("/").split("/")[-1]
            return [EpisodeItem(number="1", title="Capítulo 1", url=f"{self.base_url}/ver/{slug}-1")]
        return self._parse_episodes_from_html(anime_url, html)

    def _parse_videos_from_html(self, html: str) -> List[Dict[str, str]]:
        embeds = []
        m = re.search(r'var videos = (\[.*?\]);', html, re.DOTALL)
        if m:
            try:
                raw_videos = json.loads(m.group(1))
                for v in raw_videos:
                    if len(v) > 1 and isinstance(v[1], str) and v[1].startswith("http"):
                        embeds.append({
                            "server": str(v[0]),
                            "url": v[1],
                            "referer": f"{self.base_url}/"
                        })
            except Exception:
                pass
        return embeds

    def get_embed_urls(
        self,
        episode_url: str,
        pref_audio: str = "latino",
        episode_num: Optional[int] = None
    ) -> List[Dict[str, str]]:
        if episode_num and "/ver/" not in episode_url:
            slug = episode_url.rstrip("/").split("/")[-1]
            target_url = f"{self.base_url}/ver/{slug}-{episode_num}"
        else:
            target_url = episode_url

        html = self._fetch(target_url)
        if not html:
            return []
        return self._parse_videos_from_html(html)
