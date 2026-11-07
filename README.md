<div align="center">

# 🎬 Anime-CMD v1.7.0

**Herramienta interactiva de línea de comandos con motor agregador multi-proveedor y agrupación inteligente para buscar y reproducir anime con prioridad absoluta en Audio Latino directamente en tu terminal.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Plataforma-Windows%20%7C%20Linux%20%7C%20macOS%20%7C%20Android%20(Termux)-green.svg)]()
[![Shell](https://img.shields.io/badge/CLI-Bash%20%2B%20Python-orange.svg)]()
[![Providers](https://img.shields.io/badge/Fuentes-AnimeOnline%20%7C%20TioAnime%20%7C%20MonosChinos%20%7C%20JKAnime-blueviolet.svg)]()

</div>

---

## ⚡ Características Principales

- 🌐 **Motor Agregador Multi-Plataforma:** Escaneo concurrente y paralelo en milisegundos a través de las principales bibliotecas de anime activas:
  - 🟠 **Anime Online (AnimeOnline.Ninja)**
  - 🟣 **TioAnime**
  - 🔵 **MonosChinos**
  - 🟢 **JKAnime**
  - *(AnimeFLV desactivado temporalmente por inestabilidad de sus servidores)*
- 🌸 **Separadores por Temporada y Títulos Completos:** Navegación mejorada con bloques visuales por temporada, títulos de capítulos y búsqueda instantánea en AnimeOnline.
- 📦 **Agrupación Inteligente de Servidores:** Los animes duplicados entre múltiples plataformas se consolidan en una sola opción interactiva que muestra las insignias de todos los servidores disponibles:
  ```text
  🔊 [LAT]   [Anime Online / JKAnime]   Dragon Ball Z
  🇯🇵 [SUB]   [TioAnime / MonosChinos]   Dragon Ball Super
  ```
- 🔊 **Prioridad Absoluta en Audio Latino (`[LAT]`):** El algoritmo clasifica automáticamente todas las fuentes priorizando doblaje latino (`[LAT]`), seguido de castellano (`[CAST]`), y con fallback automático a subtitulado en japonés (`[SUB]`).
- 🚀 **Extractor Robusto con Pre-Verificación:** Resuelve y reproduce automáticamente enlaces directos y streams HLS de **Streamtape**, **Mp4upload**, **YourUpload**, **Streamwish**, **Voe.sx**, **Filemoon**, **JKPlayer (M3U8)**, **Ok.ru**, **Mega** y más con **evasión de señuelos anti-scraper, verificación HTTP previa y failover automático**.
- 🎯 **Menú Interactivo con FZF:** Navegación instantánea con atajos de teclado, selector de episodios con temporadas, lista rápida post-reproducción y cambio dinámico de servidor.
- 🕒 **Historial y Reanudación Inteligente (`-c`):** Guarda tu progreso y último minuto visto en una base de datos local SQLite para continuar exactamente donde lo dejaste.
- 💻 **Multiplataforma Real:** Compatible con **CMD**, **PowerShell**, **Windows Terminal**, **Git Bash**, **Linux**, **macOS** y **Android (Termux)**.

---

## 🚀 Instalación en 1 solo comando

El instalador automático descarga el programa y configura todas las dependencias necesarias (**MPV**, **FZF**, **Python**, **Git**).

### 🪟 Windows (PowerShell)
Abre PowerShell y ejecuta:

```powershell
irm https://raw.githubusercontent.com/HugoAleOlguin/Anime-CMD/main/install.ps1 | iex
```

### 🐧 Linux / macOS / WSL / Android (Termux)
Abre tu terminal y ejecuta:

```bash
curl -sL https://raw.githubusercontent.com/HugoAleOlguin/Anime-CMD/main/install.sh | bash
```

### 📦 Desde el Repositorio (Clonar y ejecutar en cualquier PC)
```bash
git clone https://github.com/HugoAleOlguin/Anime-CMD.git
cd Anime-CMD
pip install -r requirements.txt
anime  # o: python src/main.py
```

---

## 🎮 Modo de uso

```bash
# Modo interactivo (Búsqueda en todos los servicios, Audio Latino por defecto)
anime

# Búsqueda directa
anime evangelion
anime dragon ball
anime naruto shippuden
anime jujutsu kaisen

# Forzar versión subtitulada en japonés
anime shingeki no kyojin -s

# Continuar viendo el último anime donde lo dejaste
anime -c

# Ver ayuda y versión instalada
anime --help
anime --version

# Actualizar Anime-CMD a la última versión
anime --update
# o también:
anime -u
```

---

## 🛠️ Controles durante la reproducción (MPV)

| Tecla | Acción |
| :--- | :--- |
| <kbd>Espacio</kbd> | Pausar / Reanudar |
| <kbd>→</kbd> / <kbd>←</kbd> | Avanzar / Retroceder 5 segundos |
| <kbd>↑</kbd> / <kbd>↓</kbd> | Avanzar / Retroceder 1 minuto |
| <kbd>f</kbd> | Alternar Pantalla Completa |
| <kbd>9</kbd> / <kbd>0</kbd> | Disminuir / Aumentar volumen |
| <kbd>q</kbd> | Salir de MPV y abrir menú de acciones (Siguiente / Retroceder / Cambiar Audio) |

---

## 📂 Estructura del repositorio

```text
├── ani-es        # Script ejecutable principal y motor agregador multi-proveedor
├── anime.cmd     # Wrapper ejecutable para Windows CMD/PowerShell
├── install.ps1   # Instalador automático para Windows con gestión de dependencias
├── install.sh    # Instalador automático para Linux/macOS/Termux
└── README.md     # Documentación oficial
```

---

## 📄 Licencia

Distribuido bajo la Licencia MIT. Consulta `LICENSE` para más información.
