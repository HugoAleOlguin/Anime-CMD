#!/bin/bash
set -e
echo "Compilando Anime-CMD a binario autónomo para Linux/macOS..."
python3 -m PyInstaller --clean --noconfirm build/anime.spec

if [ -f "dist/anime" ]; then
    chmod +x dist/anime
    echo "[OK] Compilación completada con éxito en dist/anime"
else
    echo "[ERROR] No se encontró dist/anime"
    exit 1
fi
