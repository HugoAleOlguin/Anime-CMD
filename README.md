# 🎬 Anime CLI (`ani-es`)

Herramienta de línea de comandos ultrarrápida e interactiva para buscar, seleccionar y ver anime en español directamente desde tu terminal utilizando **MPV** y **FZF**.

---

## ⚡ Características

- 🔎 **Búsqueda instantánea:** Búsqueda en memoria de títulos de anime.
- 🎯 **Menú interactivo:** Selección de animes, episodios y acciones posteriores mediante `fzf`.
- 📺 **Reproducción fluida:** Soporte para streams HLS directos (`.m3u8`) a través de MPV con búfer optimizado.
- 🕒 **Historial y progreso:** Guarda automáticamente en SQLite el último capítulo visto y el minuto de progreso para continuar donde lo dejaste (`-c` / `--continue`).
- ⌨️ **UX limpia:** Compatible con <kbd>ESC</kbd> para volver atrás sin cerrar la consola, y soporte completo para CMD, PowerShell, Windows Terminal, Git Bash, Linux y Termux.

---

## 📦 Requisitos previos

Asegúrate de tener instaladas las siguientes herramientas:
- **Git** (Git Bash en Windows)
- **Python 3** (con `beautifulsoup4` opcional)
- **MPV** (reproductor de video)
- **fzf** (menú interactivo)
- **curl** / **wget** / **jq**

> 💡 **En Windows:** Puedes instalar todas las dependencias con [Scoop](https://scoop.sh):
> ```powershell
> scoop install git python mpv fzf curl wget jq
> ```

---

## 🚀 Instalación en 1 comando

### 🪟 Windows (PowerShell)
```powershell
irm https://raw.githubusercontent.com/Zhuchii/ani-es/main/install.ps1 | iex
```

### 🐧 Linux / macOS / WSL / Android (Termux)
```bash
curl -sL https://raw.githubusercontent.com/Zhuchii/ani-es/main/install.sh | bash
```

---

## 🎮 Uso

```bash
# Modo interactivo (te pedirá el nombre a buscar)
anime

# Búsqueda directa
anime evangelion
anime naruto shippuden
anime one piece

# Continuar viendo donde lo dejaste
anime -c

# Ver ayuda y versión
anime --help
anime --version
```

---

## 🛠️ Estructura del proyecto

```text
├── ani-es        # Script ejecutable principal en Bash/Python
├── anime.cmd     # Wrapper ejecutable para Windows CMD/PowerShell
├── install.ps1   # Script de instalación para Windows
├── install.sh    # Script de instalación para Linux/macOS/Termux
└── README.md     # Documentación del proyecto
```
