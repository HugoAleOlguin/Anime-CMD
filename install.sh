#!/bin/bash
set -e

echo -e "\033[0;36m==========================================\033[0m"
echo -e "\033[0;32m       Instalador de Anime CLI            \033[0m"
echo -e "\033[0;36m==========================================\033[0m"

REPO_URL="https://raw.githubusercontent.com/Zhuchii/ani-es/main"
INSTALL_DIR="/usr/local/bin"

if [ -w "$INSTALL_DIR" ]; then
    echo -e "\033[0;33m[*] Descargando anime en $INSTALL_DIR...\033[0m"
    curl -sL "$REPO_URL/ani-es" -o "$INSTALL_DIR/anime"
    chmod +x "$INSTALL_DIR/anime"
else
    USER_BIN="$HOME/.local/bin"
    mkdir -p "$USER_BIN"
    echo -e "\033[0;33m[*] Descargando anime en $USER_BIN...\033[0m"
    curl -sL "$REPO_URL/ani-es" -o "$USER_BIN/anime"
    chmod +x "$USER_BIN/anime"

    if [[ ":$PATH:" != *":$USER_BIN:"* ]]; then
        echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> "$HOME/.bashrc"
        echo -e "\033[0;33m[*] Se agregó $USER_BIN a tu PATH en ~/.bashrc\033[0m"
    fi
fi

echo -e "\033[0;32m¡Instalación completada exitosamente!\033[0m"
echo -e "\033[0;36mEscribe 'anime' en tu terminal para comenzar.\033[0m"
