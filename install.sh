#!/bin/bash
# ==============================================================================
# 🎬 Anime-CMD v2.1 - Instalador y Actualizador para Linux / macOS / Termux
# Repositorio: https://github.com/HugoAleOlguin/Anime-CMD
# ==============================================================================

set -e

echo ""
echo -e "\033[0;36m==========================================================\033[0m"
echo -e "\033[0;32m         🎬 Instalador Automático de Anime-CMD v2.1       \033[0m"
echo -e "\033[0;36m==========================================================\033[0m"
echo ""

# 1. Limpieza de versiones previas
echo -e "\033[0;36m[1/4] 🧹 Limpiando versiones y archivos previos...\033[0m"
rm -rf "$HOME/ani-es" "$HOME/.anime-cmd" "$HOME/.local/bin/ani-es" "/usr/local/bin/ani-es" 2>/dev/null || true

# 2. Instalar dependencias según el sistema (SIN wget, SIN jq)
echo -e "\033[0;36m[2/4] 🔍 Verificando dependencias del sistema...\033[0m"

if [ -n "$PREFIX" ] && [[ "$PREFIX" == *com.termux* ]]; then
    # Android Termux
    pkg update -y
    pkg install -y mpv fzf python git
    pip install --quiet beautifulsoup4 || true
elif command -v apt-get &>/dev/null; then
    # Debian / Ubuntu / Mint / PopOS
    sudo apt-get update -y
    sudo apt-get install -y mpv fzf python3 python3-pip git
    pip3 install --quiet beautifulsoup4 --break-system-packages 2>/dev/null || pip install --quiet beautifulsoup4 2>/dev/null || true
elif command -v pacman &>/dev/null; then
    # Arch Linux / Manjaro
    sudo pacman -Sy --noconfirm mpv fzf python python-pip git python-beautifulsoup4 2>/dev/null || sudo pacman -Sy --noconfirm mpv fzf python python-pip git
elif command -v dnf &>/dev/null; then
    # Fedora / RHEL
    sudo dnf install -y mpv fzf python3 python3-pip git python3-beautifulsoup4 2>/dev/null || sudo dnf install -y mpv fzf python3 python3-pip git
elif command -v brew &>/dev/null; then
    # macOS Homebrew
    brew install mpv fzf python git
    pip3 install --quiet beautifulsoup4 || true
fi

# 3. Descargar el script principal
echo -e "\033[0;36m[3/4] 📥 Instalando script principal...\033[0m"
REPO_URL="https://raw.githubusercontent.com/HugoAleOlguin/Anime-CMD/main"
TIMESTAMP=$(date +%s)
INSTALL_DIR="/usr/local/bin"

if [ -w "$INSTALL_DIR" ]; then
    rm -f "$INSTALL_DIR/anime" 2>/dev/null || true
    curl -sL -H "Cache-Control: no-cache" "$REPO_URL/ani-es?v=$TIMESTAMP" -o "$INSTALL_DIR/anime"
    chmod +x "$INSTALL_DIR/anime"
    echo -e "  \033[0;32m[✔] Ejecutable instalado en $INSTALL_DIR/anime\033[0m"
else
    USER_BIN="$HOME/.local/bin"
    mkdir -p "$USER_BIN"
    rm -f "$USER_BIN/anime" 2>/dev/null || true
    curl -sL -H "Cache-Control: no-cache" "$REPO_URL/ani-es?v=$TIMESTAMP" -o "$USER_BIN/anime"
    chmod +x "$USER_BIN/anime"
    echo -e "  \033[0;32m[✔] Ejecutable instalado en $USER_BIN/anime\033[0m"

    # 4. Configurar PATH
    if [[ ":$PATH:" != *":$USER_BIN:"* ]]; then
        echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> "$HOME/.bashrc"
        echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> "$HOME/.zshrc" 2>/dev/null || true
        echo -e "  \033[0;32m[✔] $USER_BIN añadido al PATH.\033[0m"
    fi
fi

echo ""
echo -e "\033[0;32m==========================================================\033[0m"
echo -e "\033[0;32m  ✨ ¡Instalación limpia de Anime-CMD v2.1 completada! ✨ \033[0m"
echo -e "\033[0;32m==========================================================\033[0m"
echo ""
echo -e "\033[0;36m👉 Escribe \033[1;33manime\033[0;36m en tu terminal para comenzar.\033[0m"
echo ""
