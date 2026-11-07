"""Registro y orquestador multi-proveedor concurrente con modo secreto (-hh)."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional
from src.providers.base import BaseProvider
from src.providers.animeonline import AnimeOnlineProvider
from src.providers.tioanime import TioAnimeProvider
from src.providers.monoschinos import MonosChinosProvider
from src.providers.jkanime import JKAnimeProvider
from src.providers.secret import SecretProvider
from src.core.models import AnimeResult

class ProviderRegistry:
    def __init__(self):
        self._providers: Dict[str, BaseProvider] = {
            "animeonline": AnimeOnlineProvider(),
            "tioanime": TioAnimeProvider(),
            "monoschinos": MonosChinosProvider(),
            "jkanime": JKAnimeProvider(),
        }
        self.secret_provider: BaseProvider = SecretProvider()

    def get(self, provider_id: str) -> Optional[BaseProvider]:
        if provider_id == "secret":
            return self.secret_provider
        return self._providers.get(provider_id)

    def list_providers(self) -> List[BaseProvider]:
        """Devuelve los proveedores públicos normales (sin exponer el secreto)."""
        return list(self._providers.values())

    def search_all(
        self,
        query: str,
        force_sub: bool = False,
        max_workers: int = 4,
        secret_mode: bool = False
    ) -> List[AnimeResult]:
        """Ejecuta la búsqueda en paralelo o en el proveedor secreto si secret_mode es True."""
        if secret_mode:
            try:
                return self.secret_provider.search(query, force_sub=force_sub)
            except Exception:
                return []

        all_results: List[AnimeResult] = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_provider = {
                executor.submit(prov.search, query, force_sub): p_id
                for p_id, prov in self._providers.items()
            }
            for future in as_completed(future_to_provider):
                try:
                    res = future.result()
                    if res:
                        all_results.extend(res)
                except Exception:
                    pass

        # Ordenar dando prioridad a doblaje latino y series completas sobre películas/avances
        def sort_priority(item: AnimeResult):
            # Prioridad 0: Latino, 1: Castellano, 2: Sub
            audio_prio = 0 if "LAT" in item.display_tag() else (1 if "CAST" in item.display_tag() else 2)
            # Prioridad series completas (0) vs películas/avances (1)
            t_lower = item.title.lower()
            is_movie = 1 if ("/pelicula/" in item.url or "movie" in t_lower or "pelicula" in t_lower) else 0
            # Prioridad por proveedor
            prov_prio = 0 if item.provider_id == "animeonline" else 1
            return (audio_prio, is_movie, prov_prio)

        all_results.sort(key=sort_priority)
        return all_results
