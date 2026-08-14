<div align="center">

# 🎬 Anime-CMD

**Herramienta interactiva y ultrarrápida de línea de comandos para buscar, elegir y reproducir anime en español directamente desde tu terminal.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Plataforma-Windows%20%7C%20Linux%20%7C%20macOS%20%7C%20Android%20(Termux)-green.svg)]()
[![Shell](https://img.shields.io/badge/CLI-Bash%20%2B%20Python-orange.svg)]()

</div>

---

## ⚡ Características

- 🔎 **Búsqueda instantánea en memoria:** Motor optimizado que busca y lista títulos sin retrasos ni carpetas temporales pesadas.
- 🎯 **Menú interactivo con FZF:** Navegación fluida de animes, selección de episodios y opciones posteriores.
- 📺 **Reproducción directa con MPV:** Carga y reproducción de streams HLS (`.m3u8`) con buffering inteligente.
- 🕒 **Historial y reanudación automática:** Guarda tu progreso y último capítulo visto en una base de datos local SQLite para continuar cuando quieras (`-c` / `--continue`).
- ⌨️ **UX intuitiva:** Vuelve atrás en cualquier momento con la tecla <kbd>ESC</kbd> sin cerrar la consola.
- 💻 **Multiplataforma:** Total compatibilidad con **CMD**, **PowerShell**, **Windows Terminal**, **Git Bash**, **Linux**, **macOS** y **Android (Termux)**.

---

## 🚀 Instalación en 1 solo comando

El instalador automático se encarga de descargar el programa y configurar las dependencias necesarias (**MPV**, **FZF**, **Python**, **Git**, etc.).

### 🪟 Windows (PowerShell)
Abre PowerShell y pega:

```powershell
irm https://raw.githubusercontent.com/HugoAleOlguin/Anime-CMD/main/install.ps1 | iex
```

### 🐧 Linux / macOS / WSL / Android (Termux)
Abre tu terminal y pega:

```bash
curl -sL https://raw.githubusercontent.com/HugoAleOlguin/Anime-CMD/main/install.sh | bash
```

---

## 🎮 Modo de uso

```bash
# Modo interactivo (te pedirá qué anime deseas ver)
anime

# Búsqueda directa por título
anime evangelion
anime naruto shippuden
anime one piece
anime jujutsu kaisen

# Continuar viendo el último anime donde lo dejaste
anime -c

# Ver ayuda y versión
anime --help
anime --version
```

---

## 🛠️ Controles durante la reproducción (MPV)

| Tecla | Acción |
| :--- | :--- |
| <kbd>Espacio</kbd> | Pausar / Reanudar |
| <kbd>→</kbd> / <kbd>←</kbd> | Avanzar / Retroceder 5 segundos |
| <kbd>↑</kbd> / <kbd>↓</kbd> | Avanzar / Retroceder 1 minuto |
| <kbd>f</kbd> | Pantalla completa |
| <kbd>9</kbd> / <kbd>0</kbd> | Disminuir / Aumentar volumen |
| <kbd>q</kbd> | Salir del reproductor y ver opciones del siguiente capítulo |

---

## 📂 Estructura del repositorio

```text
├── ani-es        # Script ejecutable principal (Bash + Python)
├── anime.cmd     # Wrapper ejecutable para Windows CMD/PowerShell
├── install.ps1   # Instalador automático para Windows con gestión de dependencias
├── install.sh    # Instalador automático para Linux/macOS/Termux
└── README.md     # Documentación oficial
```

---

## 📄 Licencia

Distribuido bajo la Licencia MIT. Consulta `LICENSE` para más información.
