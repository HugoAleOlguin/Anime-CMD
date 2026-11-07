"""Registro y resolutor automático de enlaces de streaming."""
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional
from src.extractors.base import BaseExtractor, verify_stream
from src.extractors.streamtape import StreamtapeExtractor
from src.extractors.streamwish import StreamwishExtractor
from src.extractors.mp4upload import Mp4uploadExtractor
from src.extractors.yourupload import YourUploadExtractor
from src.extractors.voex import VoeExtractor
from src.extractors.mediafire import MediafireExtractor
from src.core.models import StreamSource

class ExtractorRegistry:
    def __init__(self):
        self._extractors: List[BaseExtractor] = [
            StreamtapeExtractor(),
            YourUploadExtractor(),
            Mp4uploadExtractor(),
            VoeExtractor(),
            StreamwishExtractor(),
            MediafireExtractor(),
        ]

    def resolve(self, embed_url: str, referer: Optional[str] = None, check_stream: bool = True) -> Optional[StreamSource]:
        """Resuelve una URL de servidor/embed a un enlace directo reproducible."""
        if not embed_url or not isinstance(embed_url, str):
            return None

        embed_clean = embed_url.strip()
        if not (embed_clean.startswith("http://") or embed_clean.startswith("https://")):
            return None

        embed_lower = embed_clean.lower()
        if "smb:" in embed_lower or "file:" in embed_lower or embed_clean.startswith("\\\\") or "\\" in embed_clean:
            return None

        # Si ya es un enlace directo mp4 o m3u8
        if bool(re.search(r'\.(?:mp4|m3u8)(?:[?#]|$)', embed_clean.lower())):
            if not check_stream or verify_stream(embed_clean, referer=referer):
                return StreamSource(server_name="direct", stream_url=embed_clean, referer=referer)

        for extractor in self._extractors:
            if extractor.matches(embed_clean):
                source = extractor.extract(embed_clean, referer=referer)
                if source and source.stream_url:
                    if not check_stream or verify_stream(source.stream_url, referer=source.referer or referer):
                        return source

        # Fallback genérico para servidores que mpv soporta nativamente (ok.ru, filemoon, etc.)
        # Excluimos mega.nz ya que requiere cliente/claves propietarias y no es reproducible por ffmpeg/mpv
        u_lower = embed_clean.lower()
        if any(k in u_lower for k in ["ok.ru", "filemoon", "vidhide", "doodstream", "uqload"]):
            return StreamSource(server_name="generic", stream_url=embed_clean, referer=referer)

        return None

    def resolve_candidates(
        self,
        embeds: List[dict],
        max_candidates: int = 6,
        max_workers: int = 4
    ) -> List[StreamSource]:
        """
        Resuelve concurrentemente los mejores candidatos disponibles y los retorna
        priorizando fuentes directas y extractores específicos sobre servidores genéricos.
        """
        if not embeds:
            return []

        candidates = embeds[:max_candidates]
        resolved_sources: List[StreamSource] = []

        with ThreadPoolExecutor(max_workers=min(max_workers, len(candidates))) as executor:
            future_to_emb = {
                executor.submit(self.resolve, emb.get("url", ""), emb.get("referer")): emb
                for emb in candidates
            }
            for future in as_completed(future_to_emb):
                try:
                    res = future.result()
                    if res and res.stream_url:
                        resolved_sources.append(res)
                except Exception:
                    pass

        # Si aún no hay fuentes, probar con los candidatos restantes
        if not resolved_sources and len(embeds) > max_candidates:
            for emb in embeds[max_candidates:]:
                res = self.resolve(emb.get("url", ""), referer=emb.get("referer"))
                if res and res.stream_url:
                    resolved_sources.append(res)

        # Ordenar por prioridad:
        # 1. direct (.mp4 / .m3u8 verificados)
        # 2. extractores especializados (YourUpload, Streamtape, Streamwish, Mp4upload, etc.)
        # 3. generic
        def priority_score(source: StreamSource) -> int:
            if source.server_name == "direct":
                return 0
            if source.server_name != "generic":
                return 1
            return 2

        resolved_sources.sort(key=priority_score)
        return resolved_sources

    def resolve_first(self, embeds: List[dict], max_candidates: int = 5, max_workers: int = 3) -> Optional[StreamSource]:
        """
        Resuelve concurrentemente los mejores candidatos y retorna de inmediato el primer resultado válido,
        cancelando los futures pendientes sin esperar a que terminen hilos lentos o fallidos.
        """
        if not embeds:
            return None

        candidates = embeds[:max_candidates]
        executor = ThreadPoolExecutor(max_workers=min(max_workers, len(candidates)))
        try:
            future_to_emb = {
                executor.submit(self.resolve, emb.get("url", ""), emb.get("referer")): emb
                for emb in candidates
            }
            for future in as_completed(future_to_emb):
                try:
                    res = future.result()
                    if res and res.stream_url:
                        executor.shutdown(wait=False, cancel_futures=True)
                        return res
                except Exception:
                    pass
        finally:
            executor.shutdown(wait=False, cancel_futures=True)

        # Si aún no hay fuentes, probar con los candidatos restantes
        if len(embeds) > max_candidates:
            for emb in embeds[max_candidates:]:
                res = self.resolve(emb.get("url", ""), referer=emb.get("referer"))
                if res and res.stream_url:
                    return res

        return None
