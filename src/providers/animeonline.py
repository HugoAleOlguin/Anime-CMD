"""Proveedor AnimeOnline Ninja con bypass de Cloudflare (curl_cffi) y soporte de temporadas."""
import re
import json
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from typing import List, Optional
from src.providers.base import BaseProvider
from src.core.models import AnimeResult, EpisodeItem, AudioType
from src.core.config import ANIME_DIR

try:
    from curl_cffi import requests as c_requests
except ImportError:
    c_requests = None

class AnimeOnlineProvider(BaseProvider):
    name = "Anime Online"
    provider_id = "animeonline"
    base_url = "https://ww3.animeonline.ninja"

    def _cffi_get(self, url: str, timeout: int = 10, headers: Optional[dict] = None) -> Optional[str]:
        if not c_requests:
            return self.fetch_html(url, timeout=timeout)
        try:
            r = c_requests.get(url, impersonate="chrome124", timeout=timeout, headers=headers)
            if r.status_code == 200:
                return r.text
        except Exception:
            pass
        return None

    def search(self, query: str, force_sub: bool = False) -> List[AnimeResult]:
        results = []
        url = f"{self.base_url}/search/?s=" + urllib.parse.quote(query)
        html = self._cffi_get(url)
        if not html:
            return results

        soup = BeautifulSoup(html, "html.parser")
        for art in soup.select(".result-item article, article"):
            title_el = art.select_one(".title a, h3 a")
            if not title_el:
                continue

            href = title_el.get("href", "")
            if not href or "/episodio/" in href:
                continue

            title = title_el.get_text(strip=True)
            desc = art.select_one(".contenido, p")
            desc_text = desc.get_text(strip=True).lower() if desc else ""
            t_lower = title.lower()

            is_lat = "latino" in t_lower or "latino" in desc_text or "audio latino" in desc_text
            is_cast = "castellano" in t_lower or "castellano" in desc_text
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
        cache_file = ANIME_DIR / "ao_eps.json"
        req_url = anime_url.rstrip("/") + "/?s="
        html = self._cffi_get(req_url)
        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")

        # Soporte para Películas y OVAs de un solo capítulo
        if "/pelicula/" in anime_url or not soup.select(".se-c, ul.episodios li, .episodios li"):
            if soup.select("#playeroptionsul li, .playeroptions li, [data-post]"):
                title_el = soup.select_one(".data h1, h1")
                title_txt = title_el.get_text(strip=True) if title_el else "Película Completa"
                return [
                    EpisodeItem(
                        number="1",
                        title=title_txt,
                        url=anime_url,
                        season="Película"
                    )
                ]

        se_blocks = soup.select(".se-c")
        ep_items: List[EpisodeItem] = []
        cache_list = []

        if se_blocks:
            for s_idx, s in enumerate(se_blocks, 1):
                num_span = s.select_one(".se-t")
                s_num = num_span.get_text(strip=True) if num_span else str(s_idx)
                s_title = f"Temporada {s_num}"

                # Agregar cabecera de temporada para fzf
                ep_items.append(EpisodeItem(
                    number="HEADER",
                    title=s_title,
                    url=anime_url,
                    season=s_title,
                    is_season_header=True
                ))

                for li in s.select("ul.episodios li, .episodios li"):
                    a = li.find("a", href=True)
                    if not a or "/episodio/" not in a["href"]:
                        continue

                    num = li.select_one(".numerando")
                    num_txt = num.get_text(strip=True) if num else ""
                    if re.search(r"-\s*0$", num_txt) or num_txt == "0":
                        continue

                    title_el = li.select_one(".episodiotitle a, .episodiotitle")
                    title_txt = title_el.get_text(strip=True) if title_el else ""
                    title_txt = re.sub(r"[A-Za-z]{3,}\.?\s+\d{1,2},\s+\d{4}$", "", title_txt).strip()

                    href = a["href"]
                    cache_list.append(href)
                    ep_num = str(len(cache_list))

                    ep_items.append(EpisodeItem(
                        number=ep_num,
                        title=title_txt or f"Episodio {ep_num}",
                        url=href,
                        season=s_title
                    ))
        else:
            for li in soup.select("ul.episodios li, .episodios li"):
                a = li.find("a", href=True)
                if not a or "/episodio/" not in a["href"]:
                    continue

                num = li.select_one(".numerando")
                num_txt = num.get_text(strip=True) if num else ""
                if re.search(r"-\s*0$", num_txt) or num_txt == "0":
                    continue

                title_el = li.select_one(".episodiotitle a, .episodiotitle")
                title_txt = title_el.get_text(strip=True) if title_el else ""
                title_txt = re.sub(r"[A-Za-z]{3,}\.?\s+\d{1,2},\s+\d{4}$", "", title_txt).strip()

                href = a["href"]
                cache_list.append(href)
                ep_num = str(len(cache_list))

                ep_items.append(EpisodeItem(
                    number=ep_num,
                    title=title_txt or f"Episodio {ep_num}",
                    url=href,
                    season="Temporada 1"
                ))

        # Guardar en cache local para acceso veloz en streaming
        if cache_list:
            try:
                with open(cache_file, "w", encoding="utf-8") as f:
                    json.dump({"url": anime_url, "episodes": cache_list}, f)
            except Exception:
                pass

        return ep_items

    def get_embed_urls(self, episode_url: str, pref_audio: str = "latino", episode_num: Optional[int] = None) -> List[dict]:
        target_ep = episode_url
        if "/episodio/" not in target_ep and "/pelicula/" not in target_ep:
            cache_file = ANIME_DIR / "ao_eps.json"
            if cache_file.exists() and episode_num:
                try:
                    with open(cache_file, "r", encoding="utf-8") as f:
                        c_data = json.load(f)
                    if c_data.get("url") == episode_url:
                        idx = int(episode_num) - 1
                        if 0 <= idx < len(c_data.get("episodes", [])):
                            target_ep = c_data["episodes"][idx]
                except Exception:
                    pass
            if "/episodio/" not in target_ep:
                eps = self.get_episodes(episode_url)
                real_eps = [e for e in eps if not e.is_season_header]
                if episode_num and 1 <= episode_num <= len(real_eps):
                    target_ep = real_eps[episode_num - 1].url
                elif real_eps:
                    target_ep = real_eps[0].url

        req_ep = target_ep.rstrip("/") + "/?s="
        html = self._cffi_get(req_ep)
        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")
        tabs = []
        for li in soup.select("#playeroptionsul li, .playeroptions li, [data-post]"):
            p = li.get("data-post")
            n = li.get("data-nume")
            t = li.get("data-type", "tv")
            if p and n:
                tabs.append((p, n, t))

        if not tabs:
            p_matches = re.findall(r'data-post=["\'](\d+)["\']', html)
            n_matches = re.findall(r'data-nume=["\'](\d+)["\']', html)
            for p, n in zip(p_matches, n_matches):
                tabs.append((p, n, "tv"))

        embed_urls = []
        base_host = "/".join(target_ep.split("/")[:3]) if "://" in target_ep else self.base_url
        if tabs:
            def fetch_single_tab(item):
                t_post, t_nume, t_type = item
                api_url = f"{base_host}/wp-json/dooplayer/v1/post/{t_post}?type={t_type}&source={t_nume}&s="
                res = self._cffi_get(api_url, timeout=5)
                if res:
                    try:
                        return json.loads(res).get("embed_url")
                    except Exception:
                        pass
                return None

            with ThreadPoolExecutor(max_workers=min(4, len(tabs))) as executor:
                for emb in executor.map(fetch_single_tab, tabs):
                    if emb and emb not in embed_urls:
                        embed_urls.append(emb)

        target_sections = ["OD_LAT", "OD_SUB", "OD_ES"] if pref_audio == "latino" else ["OD_SUB", "OD_LAT", "OD_ES"]
        servers = []

        def ao_srv_score(u):
            ul = u.lower()
            if "streamtape" in ul: return 0
            if "mp4upload" in ul: return 1
            if "yourupload" in ul: return 2
            if "voe" in ul: return 3
            if any(k in ul for k in ["streamwish", "swdyu", "sfastwish", "wishfast", "wishembed", "strwish"]): return 4
            if "filemoon" in ul or "filemooon" in ul: return 5
            return 10

        for emb in embed_urls:
            if "saidochesto.top" in emb:
                said_html = self._cffi_get(emb, timeout=8, headers={"Referer": target_ep})
                if not said_html:
                    continue

                said_soup = BeautifulSoup(said_html, "html.parser")
                found_sections = False

                for sec in target_sections:
                    div = said_soup.find("div", class_=lambda c: c and sec in c.split())
                    sec_content = str(div) if div else ""
                    if not sec_content:
                        m_sec = re.search(
                            r'class=["\'][^"\']*' + sec + r'[^"\']*["\']>(.*?)(?:</div>\s*<div class=["\']OD|</div>\s*</div>\s*</div>)',
                            said_html,
                            re.DOTALL
                        )
                        sec_content = m_sec.group(1) if m_sec else ""

                    if sec_content:
                        found_sections = True
                        lang_label = "latino" if sec == "OD_LAT" else ("castellano" if sec == "OD_ES" else "sub")
                        links = re.findall(r"go_to_player\(['\"]([^'\"]+)['\"]\)", sec_content)
                        links.sort(key=ao_srv_score)
                        for s_url in links:
                            servers.append({
                                "server": "saidochesto",
                                "url": s_url,
                                "referer": "https://saidochesto.top/",
                                "lang": lang_label
                            })

                if not found_sections:
                    all_links = re.findall(r"go_to_player\(['\"]([^'\"]+)['\"]\)", said_html)
                    all_links.sort(key=ao_srv_score)
                    for s_url in all_links:
                        servers.append({
                            "server": "saidochesto",
                            "url": s_url,
                            "referer": "https://saidochesto.top/",
                            "lang": "sub"
                        })
            else:
                servers.append({
                    "server": "direct",
                    "url": emb,
                    "referer": target_ep,
                    "lang": "sub"
                })

        return servers
