#!/bin/bash
# ==============================================================================
# 🎬 Anime-CMD v1.7.0 - Instalador y Actualizador para Linux / macOS / Termux
# Repositorio: https://github.com/HugoAleOlguin/Anime-CMD
# ==============================================================================

set -e

echo ""
echo -e "\033[0;36m==========================================================\033[0m"
echo -e "\033[0;32m         🎬 Instalador Automático de Anime-CMD v1.7.0       \033[0m"
echo -e "\033[0;36m==========================================================\033[0m"
echo ""

# 1. Limpieza de versiones previas
echo -e "\033[0;36m[1/4] 🧹 Limpiando versiones y archivos previos...\033[0m"
rm -rf "$HOME/ani-es" "$HOME/.anime-cmd" "$HOME/.local/bin/ani-es" "/usr/local/bin/ani-es" 2>/dev/null || true
rm -f "$HOME/.anime/ao_eps.json" "$HOME/.anime/mpv_run.log" "$HOME/.anime"/*.tmp 2>/dev/null || true

# 2. Instalar dependencias según el sistema (SIN wget, SIN jq)
echo -e "\033[0;36m[2/4] 🔍 Verificando dependencias del sistema...\033[0m"

if [ -n "$PREFIX" ] && [[ "$PREFIX" == *com.termux* ]]; then
    # Android Termux
    pkg update -y
    pkg install -y mpv fzf python git
    pip install --quiet beautifulsoup4 curl_cffi || true
elif command -v apt-get &>/dev/null; then
    # Debian / Ubuntu / Mint / PopOS
    sudo apt-get update -y
    sudo apt-get install -y mpv fzf python3 python3-pip git
    pip3 install --quiet beautifulsoup4 curl_cffi --break-system-packages 2>/dev/null || pip install --quiet beautifulsoup4 curl_cffi 2>/dev/null || true
elif command -v pacman &>/dev/null; then
    # Arch Linux / Manjaro
    sudo pacman -Sy --noconfirm mpv fzf python python-pip git python-beautifulsoup4 2>/dev/null || sudo pacman -Sy --noconfirm mpv fzf python python-pip git
    pip install --quiet curl_cffi --break-system-packages 2>/dev/null || pip install --quiet curl_cffi 2>/dev/null || true
elif command -v dnf &>/dev/null; then
    # Fedora / RHEL
    sudo dnf install -y mpv fzf python3 python3-pip git python3-beautifulsoup4 2>/dev/null || sudo dnf install -y mpv fzf python3 python3-pip git
    pip3 install --quiet curl_cffi --break-system-packages 2>/dev/null || pip install --quiet curl_cffi 2>/dev/null || true
elif command -v brew &>/dev/null; then
    # macOS Homebrew
    brew install mpv fzf python git
    pip3 install --quiet beautifulsoup4 curl_cffi || true
fi

# 3. Instalar código fuente y lanzador de Anime-CMD v1.7.0
echo -e "\033[0;36m[3/4] 📥 Configurando Anime-CMD v1.7.0...\033[0m"

APP_DIR="$HOME/.anime/app"
mkdir -p "$APP_DIR"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"

if [ -d "$SCRIPT_DIR/src" ]; then
    cp -r "$SCRIPT_DIR/src" "$APP_DIR/"
    echo -e "  \033[0;32m[✔] Código fuente copiado a $APP_DIR\033[0m"
else
    if [ -d "$APP_DIR/.git" ]; then
        (cd "$APP_DIR" && git pull --quiet 2>/dev/null || true)
    else
        git clone --depth 1 --quiet "https://github.com/HugoAleOlguin/Anime-CMD.git" "$APP_DIR" 2>/dev/null || true
    fi
    echo -e "  \033[0;32m[✔] Repositorio clonado en $APP_DIR\033[0m"
fi

INSTALL_DIR="/usr/local/bin"
TARGET_DIR=""

if [ -w "$INSTALL_DIR" ]; then
    TARGET_DIR="$INSTALL_DIR"
else
    TARGET_DIR="$HOME/.local/bin"
    mkdir -p "$TARGET_DIR"
fi

LAUNCHER="$TARGET_DIR/anime"
cat << 'EOF' > "$LAUNCHER"
#!/usr/bin/env bash
APP_MAIN="$HOME/.anime/app/src/main.py"
if [ ! -f "$APP_MAIN" ]; then
    echo "[ERROR] No se encontró $APP_MAIN" >&2
    exit 1
fi
exec python3 "$APP_MAIN" "$@"
EOF

chmod +x "$LAUNCHER"
echo -e "  \033[0;32m[✔] Lanzador instalado en $LAUNCHER\033[0m"

# 4. Configurar PATH si es necesario
if [ "$TARGET_DIR" = "$HOME/.local/bin" ]; then
    if [[ ":$PATH:" != *":$TARGET_DIR:"* ]]; then
        echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> "$HOME/.bashrc"
        [ -f "$HOME/.zshrc" ] && echo "export PATH=\"\$HOME/.local/bin:\$PATH\"" >> "$HOME/.zshrc" 2>/dev/null || true
        echo -e "  \033[0;32m[✔] $TARGET_DIR añadido al PATH.\033[0m"
    fi
fi

echo ""
echo -e "\033[0;32m==========================================================\033[0m"
echo -e "\033[0;32m  ✨ ¡Instalación limpia de Anime-CMD v1.7.0 completada! ✨ \033[0m"
echo -e "\033[0;32m==========================================================\033[0m"
echo ""
echo -e "\033[0;36m👉 Escribe \033[1;33manime\033[0;36m en tu terminal para comenzar.\033[0m"
echo ""
