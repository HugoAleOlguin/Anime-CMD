"""Proveedor TioAnime."""
import re
import json
import urllib.parse
from bs4 import BeautifulSoup
from typing import List, Optional
from src.providers.base import BaseProvider
from src.core.models import AnimeResult, EpisodeItem, AudioType

class TioAnimeProvider(BaseProvider):
    name = "TioAnime"
    provider_id = "tioanime"
    base_url = "https://tioanime.com"

    def search(self, query: str, force_sub: bool = False) -> List[AnimeResult]:
        results = []
        queries = [query]
        if not force_sub and "latino" not in query.lower():
            queries.append(query + " latino")

        seen = set()
        for q in queries:
            url = f"{self.base_url}/directorio?q=" + urllib.parse.quote(q)
            html = self.fetch_html(url)
            if not html:
                continue

            soup = BeautifulSoup(html, "html.parser")
            for item in soup.select(".anime article, article.anime, li.anime"):
                a = item.find("a", href=True)
                title_el = item.find(["h3", "h2", "span"], class_="title")
                if not a or not title_el:
                    continue

                href = self.base_url + a["href"]
                if href in seen:
                    continue
                seen.add(href)

                title = title_el.get_text(strip=True)
                is_lat = bool(re.search(r"latino", title, re.I) or re.search(r"-latino/?$", href, re.I))
                is_cast = bool(re.search(r"castellano", title, re.I) or re.search(r"-castellano/?$", href, re.I))
                
                audio = AudioType.LATINO if is_lat else (AudioType.CASTELLANO if is_cast else AudioType.SUBTITULADO)
                results.append(AnimeResult(
                    title=title,
                    url=href,
                    provider_id=self.provider_id,
                    provider_name=self.name,
                    audio_type=audio
                ))
        return results

    def get_episodes(self, anime_url: str) -> List[EpisodeItem]:
        html = self.fetch_html(anime_url)
        if not html:
            return []

        m_ep = re.search(r"var episodes = (\[.*?\]);", html)
        total = 1
        if m_ep:
            try:
                eps = json.loads(m_ep.group(1))
                total = max(eps) if eps else 1
            except Exception:
                pass

        slug = anime_url.rstrip("/").split("/")[-1]
        episodes = []
        for i in range(1, total + 1):
            ep_url = f"{self.base_url}/ver/{slug}-{i}"
            episodes.append(EpisodeItem(
                number=str(i),
                title=f"Episodio {i}",
                url=ep_url
            ))
        return episodes

    def get_embed_urls(self, episode_url: str, pref_audio: str = "latino", episode_num: Optional[int] = None) -> List[dict]:
        """Obtiene la lista de servidores de streaming para el capítulo."""
        target_ep = episode_url
        if "/ver/" not in target_ep and episode_num:
            slug = episode_url.rstrip("/").split("/")[-1]
            slug_base = re.sub(r'-(?:latino|castellano)$', '', slug)
            if pref_audio == "latino":
                target_ep = f"{self.base_url}/ver/{slug_base}-latino-{episode_num}"
            else:
                target_ep = f"{self.base_url}/ver/{slug}-{episode_num}"

        html = self.fetch_html(target_ep)
        if not html and "/ver/" not in episode_url and episode_num:
            # Fallback para el otro formato
            slug = episode_url.rstrip("/").split("/")[-1]
            target_ep = f"{self.base_url}/ver/{slug}-{episode_num}"
            html = self.fetch_html(target_ep)

        if not html:
            return []

        m_vids = re.search(r"var videos = (\[.*?\]);", html)
        if not m_vids:
            return []

        try:
            videos = json.loads(m_vids.group(1))

            def srv_score(s):
                v = str(s[1]).lower() if len(s) > 1 else ""
                if "yourupload" in v: return 1
                if "voe" in v: return 2
                if "mp4upload" in v: return 3
                if "streamwish" in v: return 4
                if "ok.ru" in v: return 5
                if "mega" in v: return 6
                return 10

            videos.sort(key=srv_score)
            embeds = []
            for item in videos:
                if len(item) > 1:
                    embeds.append({
                        "server": str(item[0]),
                        "url": str(item[1]),
                        "referer": target_ep
                    })
            return embeds
        except Exception:
            return []
