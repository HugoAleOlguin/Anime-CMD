<div align="center">

# 🎬 Anime-CMD v1.7.0

**Buscá y mirá anime directamente en tu terminal, rápido, sin anuncios y con prioridad en Audio Latino.**

[![Release](https://img.shields.io/github/v/release/HugoAleOlguin/Anime-CMD?color=blue&label=Versi%C3%B3n)](https://github.com/HugoAleOlguin/Anime-CMD/releases/latest)
[![Platform](https://img.shields.io/badge/Plataforma-Windows%20%7C%20Linux%20%7C%20macOS-green.svg)]()
[![License: MIT](https://img.shields.io/badge/Licencia-MIT-orange.svg)](LICENSE)

<br/>

[**📥 Descargar anime.exe para Windows (v1.7.0)**](https://github.com/HugoAleOlguin/Anime-CMD/releases/latest/download/anime.exe)  
*(Ejecutable independiente listo para usar, no requiere Python ni configuraciones)*

</div>

---

## ⚡ Instalación rápida en 1 solo comando

### 🪟 Windows

En **PowerShell**:
```powershell
irm is.gd/animecmd | iex
```

En **CMD (Símbolo del sistema)**:
```cmd
powershell "irm is.gd/animecmd | iex"
```

---

### 🐧 Linux / 🍎 macOS / 📱 Android (Termux)

En tu terminal:
```bash
curl -sL is.gd/animecmdsh | bash
```

---

## 🎮 Modo de uso

```bash
# Modo interactivo general (Búsqueda multi-servidor y reanudación automática)
anime

# Buscar un anime directamente
anime dragon ball
anime naruto shippuden
anime jujutsu kaisen

# Continuar viendo el último anime donde lo dejaste
anime -c

# Forzar búsqueda de versiones subtituladas en japonés
anime shingeki no kyojin -s

# Ver versión instalada y ayuda
anime --version
anime --help

# Actualizar a la última versión
anime --update
```

---

## ⚡ ¿Por qué Anime-CMD?

- 🔊 **Prioridad Audio Latino (`[LAT]`):** Encuentra primero versiones dobladas al español latino, con opción de audio castellano (`[CAST]`) o subtitulado (`[SUB]`).
- 🌐 **Agregador Multi-Servidor:** Busca en simultáneo en AnimeOnline, TioAnime, MonosChinos y JKAnime, combinando opciones repetidas en un menú limpio.
- 🚀 **Cero Publicidad y Reproducción Instantánea:** Extrae y reproduce el stream directo en alta calidad sin ventanas emergentes ni acortadores molestos.
- 🕒 **Memoria Inteligente:** Guarda automáticamente por qué minuto y capítulo vas en una base local para que sigas donde te quedaste.

---

## 🛠️ Controles de reproducción (MPV)

| Tecla | Acción |
| :---: | :--- |
| <kbd>Espacio</kbd> | Pausar / Reanudar |
| <kbd>→</kbd> / <kbd>←</kbd> | Adelantar / Retroceder 5 segundos |
| <kbd>↑</kbd> / <kbd>↓</kbd> | Adelantar / Retroceder 1 minuto |
| <kbd>f</kbd> | Pantalla completa |
| <kbd>9</kbd> / <kbd>0</kbd> | Bajar / Subir volumen |
| <kbd>q</kbd> | Salir del reproductor y volver al menú |

---

## 🗑️ Desinstalación limpia

Si en algún momento querés borrarlo por completo sin dejar ningún rastro en tu sistema:

- En **Windows (PowerShell)**:
  ```powershell
  Get-Process anime, mpv -EA SilentlyContinue | Stop-Process -Force; Remove-Item -Path "$HOME\.anime" -Recurse -Force -EA SilentlyContinue; $p=[Environment]::GetEnvironmentVariable("Path","User"); $np=($p -split ';' | ? { $_ -and $_ -ne "$HOME\.anime" -and $_ -ne "$env:USERPROFILE\.anime" }) -join ';'; [Environment]::SetEnvironmentVariable("Path",$np,"User")
  ```
  *(O si tenés el archivo del proyecto, simplemente hacé doble clic en `uninstall.bat`)*

- En **Linux / macOS**:
  ```bash
  rm -rf ~/.anime ~/.local/bin/anime /usr/local/bin/anime
  ```

---

## 📄 Licencia

Distribuido bajo la Licencia MIT. Consulta `LICENSE` para más información.
