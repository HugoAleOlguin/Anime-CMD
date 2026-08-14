#!/bin/bash
# ==========================================================
# 🎬 Anime-CMD - Instalador Automático para Linux / macOS / Termux
# Repositorio: https://github.com/HugoAleOlguin/Anime-CMD
# ==========================================================

set -e

echo -e "\033[0;36m==========================================================\033[0m"
echo -e "\033[0;32m         🎬 Instalador Automático de Anime-CMD            \033[0m"
echo -e "\033[0;36m==========================================================\033[0m"
echo ""

# 1. Instalar dependencias según el gestor de paquetes del sistema
install_dependencies() {
    echo -e "\033[0;33m[*] Verificando e instalando dependencias...\033[0m"

    if [ -n "$PREFIX" ] && [[ "$PREFIX" == *com.termux* ]]; then
        # Android Termux
        pkg update -y
        pkg install -y mpv fzf python jq wget curl git
        pip install --quiet beautifulsoup4 || true
    elif command -v apt-get &>/dev/null; then
        # Debian / Ubuntu / Mint / PopOS
        sudo apt-get update -y
        sudo apt-get install -y mpv fzf python3 python3-pip jq wget curl git
        pip3 install --quiet beautifulsoup4 --break-system-packages || pip install --quiet beautifulsoup4 || true
    elif command -v pacman &>/dev/null; then
        # Arch Linux / Manjaro
        sudo pacman -Sy --noconfirm mpv fzf python python-pip jq wget curl git python-beautifulsoup4
    elif command -v dnf &>/dev/null; then
        # Fedora / RHEL
        sudo dnf install -y mpv fzf python3 python3-pip jq wget curl git python3-beautifulsoup4
    elif command -v brew &>/dev/null; then
        # macOS Homebrew
        brew install mpv fzf python jq wget curl git
        pip3 install --quiet beautifulsoup4 || true
    fi
}

install_dependencies

# 2. Descargar el script principal
REPO_URL="https://raw.githubusercontent.com/HugoAleOlguin/Anime-CMD/main"
INSTALL_DIR="/usr/local/bin"

if [ -w "$INSTALL_DIR" ]; then
    echo -e "\033[0;33m[*] Instalando ejecutable en $INSTALL_DIR/anime...\033[0m"
    curl -sL "$REPO_URL/ani-es" -o "$INSTALL_DIR/anime"
    chmod +x "$INSTALL_DIR/anime"
else
    USER_BIN="$HOME/.local/bin"
    mkdir -p "$USER_BIN"
    echo -e "\033[0;33m[*] Instalando ejecutable en $USER_BIN/anime...\033[0m"
    curl -sL "$REPO_URL/ani-es" -o "$USER_BIN/anime"
    chmod +x "$USER_BIN/anime"

    if [[ ":$PATH:" != *":$USER_BIN:"* ]]; then
        echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> "$HOME/.bashrc"
        echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> "$HOME/.zshrc" 2>/dev/null || true
        echo -e "\033[0;33m[*] $USER_BIN agregado a tu PATH.\033[0m"
    fi
fi

echo ""
echo -e "\033[0;32m==========================================================\033[0m"
echo -e "\033[0;32m  ✨ ¡Instalación de Anime-CMD completada con éxito! ✨   \033[0m"
echo -e "\033[0;32m==========================================================\033[0m"
echo ""
echo -e "\033[0;36m👉 Escribe \033[1;33manime\033[0;36m en tu terminal para comenzar.\033[0m"
echo ""
