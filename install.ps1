# ==============================================================================
# Anime-CMD v2.1 - Instalador y Actualizador Automatico para Windows
# Repositorio: https://github.com/HugoAleOlguin/Anime-CMD
# ==============================================================================

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "         Instalador Automatico de Anime-CMD v2.1          " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""

$installDir = "$HOME\.anime"

# ------------------------------------------------------------------------------
# 1. Limpieza de instalaciones anteriores
# ------------------------------------------------------------------------------
Write-Host "[1/5] Limpiando versiones y archivos temporales anteriores..." -ForegroundColor Cyan

$oldPaths = @(
    "$HOME\ani-es",
    "$HOME\.anime-cmd",
    "$HOME\AppData\Local\ani-es"
)

foreach ($old in $oldPaths) {
    if (Test-Path $old) {
        try {
            Remove-Item -Path $old -Recurse -Force -ErrorAction SilentlyContinue
            Write-Host "  -> Carpeta previa eliminada: $old" -ForegroundColor Gray
        } catch {
        }
    }
}

# Crear o limpiar directorio de instalacion principal
if (!(Test-Path $installDir)) {
    New-Item -ItemType Directory -Path $installDir -Force | Out-Null
} else {
    Remove-Item -Path "$installDir\ani-es" -Force -ErrorAction SilentlyContinue
    Remove-Item -Path "$installDir\anime.cmd" -Force -ErrorAction SilentlyContinue
    Remove-Item -Path "$installDir\anime.bat" -Force -ErrorAction SilentlyContinue
}

Write-Host "  [OK] Entorno limpio preparado en $installDir" -ForegroundColor Green

# ------------------------------------------------------------------------------
# 2. Verificacion e instalacion de dependencias necesarias
# ------------------------------------------------------------------------------
Write-Host ""
Write-Host "[2/5] Verificando dependencias esenciales..." -ForegroundColor Cyan

# Asegurar que rutas estandar de WinGet y Scoop esten en la sesion actual
$extraDirs = @(
    "$env:LOCALAPPDATA\Microsoft\WinGet\Links",
    "$env:LOCALAPPDATA\Programs\mpv",
    "C:\Program Files\mpv",
    "C:\Program Files (x86)\mpv",
    "$HOME\scoop\shims",
    "C:\ProgramData\chocolatey\bin"
)

foreach ($d in $extraDirs) {
    if ((Test-Path $d) -and ($env:Path -notlike "*$d*")) {
        $env:Path += ";$d"
    }
}

$missingDeps = @()

# Git (Git Bash)
$gitBash = $null
if (Test-Path "C:\Program Files\Git\bin\bash.exe") {
    $gitBash = "C:\Program Files\Git\bin\bash.exe"
} elseif (Test-Path "$env:LOCALAPPDATA\Programs\Git\bin\bash.exe") {
    $gitBash = "$env:LOCALAPPDATA\Programs\Git\bin\bash.exe"
} elseif (Get-Command git.exe -ErrorAction SilentlyContinue) {
    $gitCmd = (Get-Command git.exe).Source
    $possibleBash = Join-Path (Split-Path (Split-Path $gitCmd -Parent) -Parent) "bin\bash.exe"
    if (Test-Path $possibleBash) { $gitBash = $possibleBash }
}

if (!$gitBash -and !(Get-Command git.exe -ErrorAction SilentlyContinue)) {
    $missingDeps += "git"
    Write-Host "  [!] Git: NO encontrado" -ForegroundColor Yellow
} else {
    Write-Host "  [OK] Git Bash: Presente" -ForegroundColor Green
}

# Python
$hasPython = (Get-Command python.exe -ErrorAction SilentlyContinue) -or `
             (Get-Command python3.exe -ErrorAction SilentlyContinue) -or `
             (Get-Command py.exe -ErrorAction SilentlyContinue)
if (!$hasPython) {
    $missingDeps += "python"
    Write-Host "  [!] Python: NO encontrado" -ForegroundColor Yellow
} else {
    Write-Host "  [OK] Python: Presente" -ForegroundColor Green
}

# MPV
$hasMpv = (Get-Command mpv.exe -ErrorAction SilentlyContinue) -or `
          (Get-Command mpv -ErrorAction SilentlyContinue) -or `
          (Test-Path "$env:LOCALAPPDATA\Microsoft\WinGet\Links\mpv.exe") -or `
          (Test-Path "$env:LOCALAPPDATA\Programs\mpv\mpv.exe") -or `
          (Test-Path "C:\Program Files\mpv\mpv.exe") -or `
          (Test-Path "$HOME\scoop\shims\mpv.exe")

if (!$hasMpv) {
    $missingDeps += "mpv"
    Write-Host "  [!] MPV: NO encontrado" -ForegroundColor Yellow
} else {
    Write-Host "  [OK] MPV: Presente" -ForegroundColor Green
}

# FZF
$hasFzf = (Get-Command fzf.exe -ErrorAction SilentlyContinue) -or `
          (Get-Command fzf -ErrorAction SilentlyContinue) -or `
          (Test-Path "$env:LOCALAPPDATA\Microsoft\WinGet\Links\fzf.exe") -or `
          (Test-Path "$HOME\scoop\shims\fzf.exe")

if (!$hasFzf) {
    $missingDeps += "fzf"
    Write-Host "  [!] FZF: NO encontrado" -ForegroundColor Yellow
} else {
    Write-Host "  [OK] FZF: Presente" -ForegroundColor Green
}

# Instalacion automatica si falta alguna dependencia
if ($missingDeps.Count -gt 0) {
    Write-Host ""
    Write-Host "[*] Instalando dependencias faltantes automaticamente: $($missingDeps -join ', ')..." -ForegroundColor Yellow

    if (Get-Command winget.exe -ErrorAction SilentlyContinue) {
        Write-Host "-> Utilizando Windows Package Manager (WinGet)..." -ForegroundColor Cyan
        if ($missingDeps -contains "git") {
            Write-Host "   Instalando Git..." -ForegroundColor Cyan
            & winget install --id Git.Git -e --source winget --accept-package-agreements --accept-source-agreements --silent
        }
        if ($missingDeps -contains "python") {
            Write-Host "   Instalando Python..." -ForegroundColor Cyan
            & winget install --id Python.Python.3.12 -e --source winget --accept-package-agreements --accept-source-agreements --silent
        }
        if ($missingDeps -contains "mpv") {
            Write-Host "   Instalando MPV Player..." -ForegroundColor Cyan
            & winget install --id shinchiro.mpv -e --source winget --accept-package-agreements --accept-source-agreements --silent
        }
        if ($missingDeps -contains "fzf") {
            Write-Host "   Instalando FZF..." -ForegroundColor Cyan
            & winget install --id junegunn.fzf -e --source winget --accept-package-agreements --accept-source-agreements --silent
        }
    } elseif (Get-Command scoop.exe -ErrorAction SilentlyContinue) {
        Write-Host "-> Utilizando Scoop Package Manager..." -ForegroundColor Cyan
        & scoop install $missingDeps
    } else {
        Write-Host "-> Configurando Scoop para instalar dependencias de forma limpia..." -ForegroundColor Cyan
        Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
        Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression
        & scoop install $missingDeps
    }
}

# ------------------------------------------------------------------------------
# 3. Instalacion de BeautifulSoup4 en Python
# ------------------------------------------------------------------------------
Write-Host ""
Write-Host "[3/5] Configurando librerias de Python..." -ForegroundColor Cyan

if (Get-Command pip -ErrorAction SilentlyContinue) {
    & pip install --quiet beautifulsoup4 2>&1 | Out-Null
    Write-Host "  [OK] BeautifulSoup4 configurado correctamente." -ForegroundColor Green
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    & py -m pip install --quiet beautifulsoup4 2>&1 | Out-Null
    Write-Host "  [OK] BeautifulSoup4 configurado correctamente." -ForegroundColor Green
}

# ------------------------------------------------------------------------------
# 4. Descargar la version mas reciente del script principal
# ------------------------------------------------------------------------------
Write-Host ""
Write-Host "[4/5] Descargando Anime-CMD fresco desde el repositorio..." -ForegroundColor Cyan

$repoUrl = "https://raw.githubusercontent.com/HugoAleOlguin/Anime-CMD/main"
$aniScriptPath = "$installDir\ani-es"

try {
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    Invoke-WebRequest -Uri "$repoUrl/ani-es" -OutFile $aniScriptPath -UseBasicParsing
    Write-Host "  [OK] Script principal descargado con exito." -ForegroundColor Green
} catch {
    Write-Host "  [!] Reintentando descarga con WebClient..." -ForegroundColor Yellow
    $webClient = New-Object System.Net.WebClient
    $webClient.DownloadFile("$repoUrl/ani-es", $aniScriptPath)
    Write-Host "  [OK] Script principal descargado con exito." -ForegroundColor Green
}

# Crear el comando ejecutable anime.cmd
$cmdLines = @(
    "@echo off",
    "setlocal",
    "set `"PATH=%PATH%;%LOCALAPPDATA%\Microsoft\WinGet\Links;%LOCALAPPDATA%\Programs\mpv;C:\Program Files\mpv;C:\Program Files (x86)\mpv;%USERPROFILE%\scoop\shims;%USERPROFILE%\.anime`"",
    "set `"BASH_PATH=`"",
    "",
    "if exist `"C:\Program Files\Git\bin\bash.exe`" (",
    "    set `"BASH_PATH=C:\Program Files\Git\bin\bash.exe`"",
    ") else if exist `"%LOCALAPPDATA%\Programs\Git\bin\bash.exe`" (",
    "    set `"BASH_PATH=%LOCALAPPDATA%\Programs\Git\bin\bash.exe`"",
    ") else (",
    "    for %%X in (bash.exe) do (set `"BASH_PATH=%%~`$PATH:X`")",
    ")",
    "",
    "if not defined BASH_PATH (",
    "    echo [ERROR] Git Bash no fue encontrado. Asegurate de tener Git instalado.",
    "    exit /b 1",
    ")",
    "",
    "`"%BASH_PATH%`" `"%~dp0ani-es`" %*"
)

[System.IO.File]::WriteAllLines("$installDir\anime.cmd", $cmdLines)
Write-Host "  [OK] Lanzador anime.cmd generado." -ForegroundColor Green

# ------------------------------------------------------------------------------
# 5. Configurar variable de entorno PATH (incluyendo enlaces WinGet)
# ------------------------------------------------------------------------------
Write-Host ""
Write-Host "[5/5] Configurando variables de entorno..." -ForegroundColor Cyan

$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($null -eq $userPath) { $userPath = "" }

$pathsToAdd = @($installDir)
$wingetLinks = "$env:LOCALAPPDATA\Microsoft\WinGet\Links"
if (Test-Path $wingetLinks) { $pathsToAdd += $wingetLinks }

foreach ($p in $pathsToAdd) {
    if ($userPath -notlike "*$p*") {
        $userPath = if ($userPath -eq "") { $p } else { "$userPath;$p" }
        [Environment]::SetEnvironmentVariable("Path", $userPath, "User")
        $env:Path += ";$p"
        Write-Host "  [OK] $p anadido a tu variable PATH." -ForegroundColor Green
    }
}

Write-Host "  [OK] Variables de entorno listas." -ForegroundColor Green

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "  Instalacion limpia de Anime-CMD v2.1 completada!        " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Abre una nueva ventana de terminal (CMD o PowerShell) y ejecuta:" -ForegroundColor Cyan
Write-Host "   anime" -ForegroundColor Yellow
Write-Host ""
