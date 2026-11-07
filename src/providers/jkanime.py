"""Proveedor JKAnime."""
import re
import json
import base64
import urllib.parse
from bs4 import BeautifulSoup
from typing import List, Optional
from src.providers.base import BaseProvider
from src.core.models import AnimeResult, EpisodeItem, AudioType

class JKAnimeProvider(BaseProvider):
    name = "JKAnime"
    provider_id = "jkanime"
    base_url = "https://jkanime.net"

    def search(self, query: str, force_sub: bool = False) -> List[AnimeResult]:
        results = []
        queries = [query]
        if not force_sub and "latino" not in query.lower():
            queries.append(query + " latino")

        ignore_urls = {
            f"{self.base_url}/directorio/",
            f"{self.base_url}/horario/",
            f"{self.base_url}/estrenos/",
            f"{self.base_url}/top/",
            f"{self.base_url}/buscar/"
        }
        seen = set()

        for q in queries:
            url = f"{self.base_url}/buscar/" + urllib.parse.quote(q.replace(" ", "_")) + "/"
            html = self.fetch_html(url)
            if not html:
                continue

            soup = BeautifulSoup(html, "html.parser")
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if re.match(r"^https://jkanime\.net/[a-zA-Z0-9\-]+/$", href):
                    if href in ignore_urls or href in seen or a.find("div"):
                        continue
                    title = " ".join(a.get_text(" ", strip=True).split())
                    if not title or re.match(r"^\d+\s*/", title):
                        continue

                    seen.add(href)
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

        ep_nums = [int(n) for n in re.findall(r'href=["\']' + re.escape(anime_url.rstrip("/") + "/") + r'(\d+)/?["\']', html)]
        total = max(ep_nums) if ep_nums else 1

        episodes = []
        base = anime_url.rstrip("/")
        for i in range(1, total + 1):
            ep_url = f"{base}/{i}/"
            episodes.append(EpisodeItem(
                number=str(i),
                title=f"Episodio {i}",
                url=ep_url
            ))
        return episodes

    def get_embed_urls(self, episode_url: str, pref_audio: str = "latino", episode_num: Optional[int] = None) -> List[dict]:
        target_ep = episode_url
        if not re.search(r'/\d+/?$', target_ep) and episode_num:
            target_ep = f"{episode_url.rstrip('/')}/{episode_num}/"

        html = self.fetch_html(target_ep)
        if not html:
            return []

        target_lang = "3" if pref_audio == "latino" else "1"
        fallback_lang = "1" if pref_audio == "latino" else "3"

        embeds = []
        m_servers = re.search(r"var servers = (\[.*?\]);", html, re.DOTALL)
        if m_servers:
            try:
                servers_json = json.loads(m_servers.group(1))
                target = [s for s in servers_json if str(s.get("lang")) == target_lang]
                if not target:
                    target = [s for s in servers_json if str(s.get("lang")) == fallback_lang]
                if not target:
                    target = servers_json

                for s in target:
                    remote_b64 = s.get("remote", "")
                    if remote_b64:
                        try:
                            dec = base64.b64decode(remote_b64).decode("utf-8").strip()
                            embeds.append({
                                "server": s.get("server", "desconocido"),
                                "url": dec,
                                "referer": target_ep
                            })
                        except Exception:
                            pass
            except Exception:
                pass
        return embeds
