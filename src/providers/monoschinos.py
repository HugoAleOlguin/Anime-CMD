"""Proveedor MonosChinos."""
import re
import base64
import urllib.parse
from bs4 import BeautifulSoup
from typing import List, Optional
from src.providers.base import BaseProvider
from src.core.models import AnimeResult, EpisodeItem, AudioType

class MonosChinosProvider(BaseProvider):
    name = "MonosChinos"
    provider_id = "monoschinos"
    base_url = "https://monoschinos2.net"

    def search(self, query: str, force_sub: bool = False) -> List[AnimeResult]:
        results = []
        queries = [query]
        if not force_sub and "latino" not in query.lower():
            queries.append(query + " latino")

        seen = set()
        for q in queries:
            url = f"{self.base_url}/buscar?q=" + urllib.parse.quote(q)
            html = self.fetch_html(url)
            if not html:
                continue

            soup = BeautifulSoup(html, "html.parser")
            for a in soup.find_all("a", href=True):
                if "/anime/" not in a["href"]:
                    continue

                href = a["href"]
                if not href.startswith("http"):
                    href = self.base_url + href
                if href in seen:
                    continue
                seen.add(href)

                img = a.find("img", alt=True)
                title_tag = a.find(["h3", "h2", "h4", "h5", "span", "p"], class_=re.compile(r"title|name|nombre", re.I))
                if title_tag and title_tag.get_text(strip=True):
                    title = title_tag.get_text(strip=True)
                elif img and img.get("alt"):
                    title = img["alt"].strip()
                else:
                    title = a.get_text(" ", strip=True)

                title = re.sub(r"^(Anime|Pelicula|OVA|ONA|Donghua)\s*", "", title, flags=re.I).strip()
                title = re.sub(r"\s*\b(19\d\d|20\d\d)\b.*$", "", title).strip()
                title = " ".join(title.split())

                is_lat = bool(re.search(r"latino", title, re.I) or re.search(r"-audio-latino|-latino", href, re.I))
                is_cast = bool(re.search(r"castellano", title, re.I) or re.search(r"-castellano", href, re.I))
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

        ep_nums = [int(n) for n in re.findall(r"episodio-(\d+)", html)]
        total = max(ep_nums) if ep_nums else 1

        slug = anime_url.rstrip("/").split("/")[-1]
        episodes = []
        for i in range(1, total + 1):
            ep_url = f"{self.base_url}/ver/{slug}-episodio-{i}"
            episodes.append(EpisodeItem(
                number=str(i),
                title=f"Episodio {i}",
                url=ep_url
            ))
        return episodes

    def get_embed_urls(self, episode_url: str, pref_audio: str = "latino", episode_num: Optional[int] = None) -> List[dict]:
        target_ep = episode_url
        if "/ver/" not in target_ep and episode_num:
            slug = episode_url.rstrip("/").split("/")[-1]
            slug_base = re.sub(r'-(?:sub-espanol|audio-latino|castellano)$', '', slug)
            if pref_audio == "latino":
                target_ep = f"{self.base_url}/ver/{slug_base}-audio-latino-episodio-{episode_num}"
            else:
                target_ep = f"{self.base_url}/ver/{slug}-episodio-{episode_num}"

        html = self.fetch_html(target_ep)
        if not html and "/ver/" not in episode_url and episode_num:
            slug = episode_url.rstrip("/").split("/")[-1]
            target_ep = f"{self.base_url}/ver/{slug}-episodio-{episode_num}"
            html = self.fetch_html(target_ep)

        if not html:
            return []

        embeds = []
        m_btns = re.findall(r'data-player=["\']([^"\']+)["\']', html)
        decoded_servers = []
        for b in m_btns:
            try:
                dec = base64.b64decode(b).decode("utf-8", errors="ignore").strip()
                if dec.startswith("http"):
                    decoded_servers.append(dec)
            except Exception:
                pass

        def mc_srv_score(u):
            u_l = u.lower()
            if "mp4upload" in u_l: return 1
            if "yourupload" in u_l: return 2
            if "voe.sx" in u_l or "voe" in u_l: return 3
            if "streamwish" in u_l or "swdyu" in u_l: return 4
            if "filemoon" in u_l: return 5
            if "ok.ru" in u_l: return 6
            if "uqload" in u_l: return 7
            return 10

        decoded_servers.sort(key=mc_srv_score)
        for srv in decoded_servers:
            embeds.append({
                "server": "monoschinos",
                "url": srv,
                "referer": target_ep
            })
        return embeds
