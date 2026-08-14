# ==========================================================
# 🎬 Anime-CMD - Instalador Automático para Windows
# Repositorio: https://github.com/HugoAleOlguin/Anime-CMD
# ==========================================================

$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "         🎬 Instalador Automático de Anime-CMD            " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Definir directorio de instalación
$installDir = "$HOME\.anime"
if (!(Test-Path $installDir)) {
    New-Item -ItemType Directory -Path $installDir -Force | Out-Null
}

# 2. Verificar e instalar gestor de paquetes si faltan dependencias
$missingDeps = @()

if (!(Get-Command git -ErrorAction SilentlyContinue) -and !(Test-Path "C:\Program Files\Git\bin\bash.exe")) {
    $missingDeps += "git"
}
if (!(Get-Command python -ErrorAction SilentlyContinue) -and !(Get-Command python3 -ErrorAction SilentlyContinue)) {
    $missingDeps += "python"
}
if (!(Get-Command mpv -ErrorAction SilentlyContinue) -and !(Get-Command mpv.exe -ErrorAction SilentlyContinue)) {
    $missingDeps += "mpv"
}
if (!(Get-Command fzf -ErrorAction SilentlyContinue) -and !(Get-Command fzf.exe -ErrorAction SilentlyContinue)) {
    $missingDeps += "fzf"
}
if (!(Get-Command jq -ErrorAction SilentlyContinue) -and !(Get-Command jq.exe -ErrorAction SilentlyContinue)) {
    $missingDeps += "jq"
}
if (!(Get-Command wget -ErrorAction SilentlyContinue) -and !(Get-Command wget.exe -ErrorAction SilentlyContinue)) {
    $missingDeps += "wget"
}

if ($missingDeps.Count -gt 0) {
    Write-Host "[*] Dependencias faltantes detectadas: $($missingDeps -join ', ')" -ForegroundColor Yellow
    Write-Host "[*] Instalando dependencias necesarias automáticamente..." -ForegroundColor Cyan

    # Intentar con Scoop si está disponible o instalar Scoop
    if (Get-Command scoop -ErrorAction SilentlyContinue) {
        Write-Host "-> Usando Scoop para instalar dependencias..." -ForegroundColor Green
        scoop install git python mpv fzf jq wget curl
    }
    elseif (Get-Command winget -ErrorAction SilentlyContinue) {
        Write-Host "-> Usando WinGet para instalar dependencias..." -ForegroundColor Green
        if ($missingDeps -contains "git") { winget install --id Git.Git -e --source winget --accept-package-agreements --accept-source-agreements --silent }
        if ($missingDeps -contains "python") { winget install --id Python.Python.3.12 -e --source winget --accept-package-agreements --accept-source-agreements --silent }
        if ($missingDeps -contains "mpv") { winget install --id shinchiro.mpv -e --source winget --accept-package-agreements --accept-source-agreements --silent }
        if ($missingDeps -contains "fzf") { winget install --id junegunn.fzf -e --source winget --accept-package-agreements --accept-source-agreements --silent }
        if ($missingDeps -contains "jq") { winget install --id jqlang.jq -e --source winget --accept-package-agreements --accept-source-agreements --silent }
        if ($missingDeps -contains "wget") { winget install --id JernejSimoncic.Wget -e --source winget --accept-package-agreements --accept-source-agreements --silent }
    }
    else {
        Write-Host "-> Instalando Scoop para gestionar dependencias de forma limpia..." -ForegroundColor Green
        Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
        Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression
        scoop install git python mpv fzf jq wget curl
    }
} else {
    Write-Host "[✔] Todas las dependencias principales están presentes." -ForegroundColor Green
}

# Instalar BeautifulSoup para Python si Python está presente
if (Get-Command pip -ErrorAction SilentlyContinue) {
    Write-Host "[*] Verificando módulo BeautifulSoup4 en Python..." -ForegroundColor Cyan
    pip install --quiet beautifulsoup4 2>$null
}

# 3. Descargar el script principal desde tu repositorio
$repoUrl = "https://raw.githubusercontent.com/HugoAleOlguin/Anime-CMD/main"
Write-Host "[*] Descargando la última versión de Anime-CMD..." -ForegroundColor Cyan
Invoke-WebRequest -Uri "$repoUrl/ani-es" -OutFile "$installDir\ani-es" -UseBasicParsing

# 4. Crear el comando ejecutable anime.cmd
$cmdContent = @"
@echo off
setlocal
set "BASH_PATH="

if exist "C:\Program Files\Git\bin\bash.exe" (
    set "BASH_PATH=C:\Program Files\Git\bin\bash.exe"
) else (
    for %%X in (bash.exe) do (set "BASH_PATH=%%~`$PATH:X")
)

if not defined BASH_PATH (
    echo [ERROR] Git Bash no fue encontrado. Asegurate de tener Git instalado.
    exit /b 1
)

"%BASH_PATH%" "$installDir\ani-es" %*
"@

Set-Content -Path "$installDir\anime.cmd" -Value $cmdContent -Encoding ASCII

# 5. Agregar $installDir al PATH del usuario si no está presente
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($userPath -notlike "*$installDir*") {
    [Environment]::SetEnvironmentVariable("Path", "$userPath;$installDir", "User")
    $env:Path += ";$installDir"
    Write-Host "[✔] $installDir añadido a tu variable de entorno PATH." -ForegroundColor Green
}

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "  ✨ ¡Instalación de Anime-CMD completada con éxito! ✨   " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
Write-Host ""
Write-Host "👉 Abre una nueva ventana de CMD o PowerShell y escribe:" -ForegroundColor Cyan
Write-Host "   anime" -ForegroundColor Yellow
Write-Host ""
