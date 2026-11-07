"""Benchmark y pruebas exactas de flujo de Anime-CMD.
Analiza tiempos de respuesta, calidad de video, formato de audio,
prioridad de doblaje y velocidad de ejecución con MPV.
"""
import sys
import os
import time
import json
import re
import subprocess
from pathlib import Path
from typing import Dict, Any, List

sys.path.insert(0, os.path.abspath("."))

from src.core.models import AudioType
from src.providers.registry import ProviderRegistry
from src.extractors.registry import ExtractorRegistry
from src.core.player import MPVPlayer

def probe_stream_with_mpv(mpv_path: str, stream_url: str, referer: str = None) -> Dict[str, Any]:
    """Ejecuta mpv en modo headless para inspeccionar resolución, codecs y audio."""
    cmd = [
        mpv_path,
        "--vo=null",
        "--ao=null",
        "--frames=1",
        "--msg-level=all=v",
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    ]
    if referer:
        cmd.append(f"--referrer={referer}")
    cmd.append(stream_url)

    t0 = time.perf_counter()
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    t_demux = round(time.perf_counter() - t0, 3)

    out = res.stdout + res.stderr
    
    # Parsear resolución de video: ej. 1920x1080 o 1280x720
    m_res = re.search(r"VIDEO:\s*\[[a-zA-Z0-9]+\]\s*(\d+x\d+)", out)
    if not m_res:
        m_res = re.search(r"(\d{3,4}x\d{3,4})", out)
    resolution = m_res.group(1) if m_res else "Desconocida"

    # Parsear codec de video
    m_vcodec = re.search(r"Selected video codec:\s*([^\r\n]+)", out)
    vcodec = m_vcodec.group(1).strip() if m_vcodec else "h264"

    # Parsear codec y canales de audio
    m_acodec = re.search(r"Selected audio codec:\s*([^\r\n]+)", out)
    acodec = m_acodec.group(1).strip() if m_acodec else "aac"

    m_audio_info = re.search(r"AUDIO:\s*(\d+\s*Hz[^\r\n]+)", out)
    audio_info = m_audio_info.group(1).strip() if m_audio_info else "48000 Hz, stereo"

    return {
        "demux_time_sec": t_demux,
        "resolution": resolution,
        "video_codec": vcodec,
        "audio_codec": acodec,
        "audio_info": audio_info,
        "exit_code": res.returncode
    }

def run_benchmarks():
    provider_reg = ProviderRegistry()
    extractor_reg = ExtractorRegistry()
    player = MPVPlayer()

    mpv_path = player.mpv_path
    print("=" * 70)
    print("⚡ SUITE DE PRUEBAS DE FLUJO, RENDIMIENTO Y CALIDAD DE ANIME-CMD")
    print(f"🎯 MPV detectado: {mpv_path}")
    print("=" * 70)

    test_targets = [
        {"query": "rezero", "test_ep": 1, "test_last": True, "label": "Re:Zero"},
        {"query": "tokyo rev", "test_ep": 1, "test_last": True, "label": "Tokyo Revengers"},
        {"query": "naruto", "test_ep": 1, "test_last": False, "label": "Naruto"}
    ]

    report = []

    for target in test_targets:
        q = target["query"]
        print(f"\n▶ TEST FLUJO: '{q}' ({target['label']})")
        
        # 1. Búsqueda concurrente
        t0 = time.perf_counter()
        results = provider_reg.search_all(q, force_sub=False)
        t_search = round(time.perf_counter() - t0, 3)
        print(f"  [1/4] Búsqueda concurrente en todos los proveedores: {t_search}s ({len(results)} animes encontrados)")

        if not results:
            print("  ❌ Sin resultados.")
            continue

        # Primer resultado
        best_anime = results[0]
        prov = provider_reg.get(best_anime.provider_id)
        print(f"        Top match: '{best_anime.title}' | Proveedor: {best_anime.provider_name} | Audio: {best_anime.audio_type.value}")

        # 2. Carga de lista de capítulos y temporadas
        t0 = time.perf_counter()
        episodes = prov.get_episodes(best_anime.url)
        t_eps = round(time.perf_counter() - t0, 3)
        real_eps = [e for e in episodes if not e.is_season_header and e.number.isdigit()]
        season_headers = [e for e in episodes if e.is_season_header]
        print(f"  [2/4] Carga de episodios: {t_eps}s (Total: {len(real_eps)} capítulos, {len(season_headers)} temporadas)")

        # 3. Prueba de extracción de stream para Capítulo 1 (Audio Latino)
        ep1 = real_eps[0] if real_eps else None
        if not ep1:
            print("  ❌ No se encontraron capítulos.")
            continue

        print(f"\n  [3/4] Extrayendo transmisión para Capítulo {ep1.number} (Modo: AUDIO LATINO prioritario)...")
        t0 = time.perf_counter()
        embeds_lat = prov.get_embed_urls(ep1.url, pref_audio="latino", episode_num=int(ep1.number))
        t_embeds_lat = round(time.perf_counter() - t0, 3)
        print(f"        Embeds encontrados: {len(embeds_lat)} en {t_embeds_lat}s")

        t0 = time.perf_counter()
        stream_lat = extractor_reg.resolve_first(embeds_lat)
        t_resolve_lat = round(time.perf_counter() - t0, 3)

        if stream_lat and stream_lat.stream_url:
            print(f"        ✔ Stream resuelto ({stream_lat.server_name}) en {t_resolve_lat}s")
            print(f"        URL: {stream_lat.stream_url[:75]}...")
        else:
            print(f"        ❌ No se pudo resolver stream para audio latino.")

        # 4. Prueba con Subtitulado (-s)
        print(f"\n  [4/4] Probando con opción -s (JAPONÉS SUBTITULADO)...")
        t0 = time.perf_counter()
        embeds_sub = prov.get_embed_urls(ep1.url, pref_audio="sub", episode_num=int(ep1.number))
        stream_sub = extractor_reg.resolve_first(embeds_sub)
        t_resolve_sub = round(time.perf_counter() - t0, 3)

        if stream_sub and stream_sub.stream_url:
            print(f"        ✔ Stream SUB resuelto ({stream_sub.server_name}) en {t_resolve_sub}s")
        else:
            print(f"        ❌ No se pudo resolver stream sub.")

        # 5. Probar decodificación con MPV en headless
        mpv_metrics = None
        if stream_lat and stream_lat.stream_url and mpv_path:
            print(f"\n  [MPV Probe] Analizando decodificación de video/audio en MPV...")
            try:
                mpv_metrics = probe_stream_with_mpv(mpv_path, stream_lat.stream_url, referer=stream_lat.referer)
                print(f"        Resolución: {mpv_metrics['resolution']}")
                print(f"        Codec Video: {mpv_metrics['video_codec']}")
                print(f"        Codec Audio: {mpv_metrics['audio_codec']}")
                print(f"        Detalles Audio: {mpv_metrics['audio_info']}")
                print(f"        Tiempo de demuxer/primer frame: {mpv_metrics['demux_time_sec']}s")
            except Exception as e:
                print(f"        Error en probe MPV: {e}")

        # Si se solicitó probar último episodio
        last_metrics = None
        if target["test_last"] and len(real_eps) > 1:
            last_ep = real_eps[-1]
            print(f"\n  [Prueba de Borde] Probando ÚLTIMO capítulo ({last_ep.number} - {last_ep.title})...")
            t0 = time.perf_counter()
            embeds_last = prov.get_embed_urls(last_ep.url, pref_audio="latino", episode_num=int(last_ep.number))
            stream_last = extractor_reg.resolve_first(embeds_last)
            t_last_resolve = round(time.perf_counter() - t0, 3)
            if stream_last:
                print(f"        ✔ Último capítulo resuelto ({stream_last.server_name}) en {t_last_resolve}s")
                last_metrics = {"number": last_ep.number, "server": stream_last.server_name, "time": t_last_resolve}
            else:
                print(f"        ❌ Fallo al resolver último capítulo.")

        report.append({
            "target": target["label"],
            "query": q,
            "provider": best_anime.provider_name,
            "audio_detected": best_anime.audio_type.value,
            "search_time": t_search,
            "ep_load_time": t_eps,
            "total_episodes": len(real_eps),
            "latino_resolve_time": t_resolve_lat if stream_lat else None,
            "latino_server": stream_lat.server_name if stream_lat else None,
            "sub_resolve_time": t_resolve_sub if stream_sub else None,
            "sub_server": stream_sub.server_name if stream_sub else None,
            "mpv_metrics": mpv_metrics,
            "last_ep_metrics": last_metrics
        })

    # Guardar reporte en JSON para métricas exactas
    report_file = Path("tests/benchmark_results.json")
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 70)
    print("📊 RESUMEN GENERAL DE BENCHMARK Y RENDIMIENTO")
    print("=" * 70)
    for r in report:
        print(f"\nAnime: {r['target']} ({r['provider']})")
        print(f"  • Búsqueda: {r['search_time']}s | Carga {r['total_episodes']} caps: {r['ep_load_time']}s")
        if r['latino_resolve_time']:
            print(f"  • Stream Latino: {r['latino_server']} resuelto en {r['latino_resolve_time']}s")
        if r['sub_resolve_time']:
            print(f"  • Stream Subtitulado: {r['sub_server']} resuelto en {r['sub_resolve_time']}s")
        if r.get('mpv_metrics'):
            m = r['mpv_metrics']
            print(f"  • Calidad Video: {m['resolution']} ({m['video_codec']}) | Audio: {m['audio_codec']} ({m['audio_info']})")
            print(f"  • Buffer MPV inicial: {m['demux_time_sec']}s")
        if r.get('last_ep_metrics'):
            lm = r['last_ep_metrics']
            print(f"  • Último Capítulo (#{lm['number']}): {lm['server']} resuelto en {lm['time']}s")

if __name__ == "__main__":
    run_benchmarks()
