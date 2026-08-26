# ==============================================================================
# Anime-CMD v2.1 - Instalador y Actualizador Automatico para Windows
# Repositorio: https://github.com/HugoAleOlguin/Anime-CMD
# ==============================================================================

$ErrorActionPreference = "Continue"
$ProgressPreference = "SilentlyContinue"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "         Instalador Automatico de Anime-CMD v2.1          " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""

$installDir = "$HOME\.anime"

# ------------------------------------------------------------------------------
# 1. Limpieza de instalaciones anteriores y conflictos
# ------------------------------------------------------------------------------
Write-Host "[1/5] Limpiando versiones y archivos temporales anteriores..." -ForegroundColor Cyan

$oldPaths = @(
    "$HOME\ani-es",
    "$HOME\.anime-cmd",
    "$HOME\AppData\Local\ani-es",
    "$HOME\scoop\apps\ani-es",
    "$HOME\scoop\shims\anime.cmd",
    "$HOME\scoop\shims\anime",
    "$HOME\scoop\shims\ani-es.cmd",
    "$HOME\scoop\shims\ani-es",
    "$HOME\.local\bin\anime",
    "$HOME\.local\bin\ani-es"
)

foreach ($old in $oldPaths) {
    if (Test-Path $old) {
        try {
            Remove-Item -Path $old -Recurse -Force -ErrorAction SilentlyContinue
            Write-Host "  -> Elemento previo eliminado: $old" -ForegroundColor Gray
        } catch {
        }
    }
}

# Crear o preparar directorio de instalacion principal
if (!(Test-Path $installDir)) {
    New-Item -ItemType Directory -Path $installDir -Force | Out-Null
} else {
    Remove-Item -Path "$installDir\ani-es" -Force -ErrorAction SilentlyContinue
    Remove-Item -Path "$installDir\anime.cmd" -Force -ErrorAction SilentlyContinue
    Remove-Item -Path "$installDir\anime.bat" -Force -ErrorAction SilentlyContinue
}

Write-Host "  [OK] Entorno limpio preparado en $installDir" -ForegroundColor Green

# ------------------------------------------------------------------------------
# 2. Funciones auxiliares de localizacion de ejecutables
# ------------------------------------------------------------------------------
function Find-MpvExe {
    if (Get-Command mpv.exe -ErrorAction SilentlyContinue) {
        return (Get-Command mpv.exe).Source
    }
    if (Get-Command mpv -ErrorAction SilentlyContinue) {
        return (Get-Command mpv).Source
    }
    
    $searchLocations = @(
        "$installDir\mpv.exe",
        "$env:LOCALAPPDATA\Microsoft\WinGet\Links\mpv.exe",
        "$env:LOCALAPPDATA\Programs\mpv\mpv.exe",
        "C:\Program Files\mpv\mpv.exe",
        "C:\Program Files (x86)\mpv\mpv.exe",
        "$HOME\scoop\shims\mpv.exe",
        "$HOME\scoop\apps\mpv\current\mpv.exe",
        "C:\ProgramData\chocolatey\bin\mpv.exe"
    )
    
    foreach ($loc in $searchLocations) {
        if (Test-Path $loc) {
            return $loc
        }
    }
    
    # Buscar recursivamente en WinGet Packages si existe
    $wingetPkg = "$env:LOCALAPPDATA\Microsoft\WinGet\Packages"
    if (Test-Path $wingetPkg) {
        $found = Get-ChildItem -Path $wingetPkg -Filter "mpv.exe" -Recurse -File -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($found) {
            return $found.FullName
        }
    }
    
    return $null
}

function Find-FzfExe {
    if (Get-Command fzf.exe -ErrorAction SilentlyContinue) {
        return (Get-Command fzf.exe).Source
    }
    if (Get-Command fzf -ErrorAction SilentlyContinue) {
        return (Get-Command fzf).Source
    }
    
    $searchLocations = @(
        "$installDir\fzf.exe",
        "$env:LOCALAPPDATA\Microsoft\WinGet\Links\fzf.exe",
        "$HOME\scoop\shims\fzf.exe",
        "C:\ProgramData\chocolatey\bin\fzf.exe"
    )
    
    foreach ($loc in $searchLocations) {
        if (Test-Path $loc) {
            return $loc
        }
    }
    
    $wingetPkg = "$env:LOCALAPPDATA\Microsoft\WinGet\Packages"
    if (Test-Path $wingetPkg) {
        $found = Get-ChildItem -Path $wingetPkg -Filter "fzf.exe" -Recurse -File -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($found) {
            return $found.FullName
        }
    }
    
    return $null
}

# ------------------------------------------------------------------------------
# 3. Verificacion e instalacion de dependencias necesarias
# ------------------------------------------------------------------------------
Write-Host ""
Write-Host "[2/5] Verificando dependencias esenciales..." -ForegroundColor Cyan

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
    Write-Host "  [!] Git: NO encontrado, instalando..." -ForegroundColor Yellow
    if (Get-Command winget.exe -ErrorAction SilentlyContinue) {
        & winget install --id Git.Git -e --source winget --accept-package-agreements --accept-source-agreements --silent
    }
} else {
    Write-Host "  [OK] Git Bash: Presente" -ForegroundColor Green
}

# Python
$hasPython = (Get-Command python.exe -ErrorAction SilentlyContinue) -or `
             (Get-Command python3.exe -ErrorAction SilentlyContinue) -or `
             (Get-Command py.exe -ErrorAction SilentlyContinue)
if (!$hasPython) {
    Write-Host "  [!] Python: NO encontrado, instalando..." -ForegroundColor Yellow
    if (Get-Command winget.exe -ErrorAction SilentlyContinue) {
        & winget install --id Python.Python.3.12 -e --source winget --accept-package-agreements --accept-source-agreements --silent
    }
} else {
    Write-Host "  [OK] Python: Presente" -ForegroundColor Green
}

# FZF
$fzfPath = Find-FzfExe
if (!$fzfPath) {
    Write-Host "  [*] Instalando FZF de forma autonoma..." -ForegroundColor Cyan
    try {
        $fzfZip = "$env:TEMP\fzf_download.zip"
        Invoke-WebRequest -Uri "https://github.com/junegunn/fzf/releases/download/v0.60.3/fzf-0.60.3-windows_amd64.zip" -OutFile $fzfZip -UseBasicParsing
        Expand-Archive -Path $fzfZip -DestinationPath $installDir -Force
        Remove-Item -Path $fzfZip -Force -ErrorAction SilentlyContinue
        $fzfPath = "$installDir\fzf.exe"
    } catch {
        if (Get-Command winget.exe -ErrorAction SilentlyContinue) {
            & winget install --id junegunn.fzf -e --source winget --accept-package-agreements --accept-source-agreements --silent
            $fzfPath = Find-FzfExe
        }
    }
}

if ($fzfPath) {
    Write-Host "  [OK] FZF: Presente ($fzfPath)" -ForegroundColor Green
    if ($fzfPath -ne "$installDir\fzf.exe" -and (Test-Path $fzfPath)) {
        try {
            Copy-Item -Path $fzfPath -Destination "$installDir\fzf.exe" -Force -ErrorAction SilentlyContinue
        } catch {}
    }
} else {
    Write-Host "  [!] FZF: No se pudo configurar automaticamente." -ForegroundColor Yellow
}

# MPV
$mpvPath = Find-MpvExe
if (!$mpvPath) {
    Write-Host "  [*] Instalando MPV Player de forma autonoma..." -ForegroundColor Cyan
    
    # 1. Descarga directa standalone de MPV
    try {
        $mpv7z = "$env:TEMP\mpv_download.7z"
        Write-Host "    -> Descargando paquete optimizado de MPV..." -ForegroundColor Cyan
        Invoke-WebRequest -Uri "https://github.com/shinchiro/mpv-winbuild-cmake/releases/download/20260814/mpv-x86_64-20260814-git-7b8915bc1d.7z" -OutFile $mpv7z -UseBasicParsing
        & tar -xf $mpv7z -C $installDir
        Remove-Item -Path $mpv7z -Force -ErrorAction SilentlyContinue
        if (Test-Path "$installDir\mpv.exe") {
            $mpvPath = "$installDir\mpv.exe"
        }
    } catch {
        # Fallback a WinGet o Scoop si la descarga directa fallara
        if (Get-Command winget.exe -ErrorAction SilentlyContinue) {
            Write-Host "    -> Intentando WinGet..." -ForegroundColor Cyan
            & winget install --id shinchiro.mpv -e --source winget --accept-package-agreements --accept-source-agreements --silent
            $mpvPath = Find-MpvExe
        }
        if (!$mpvPath) {
            Write-Host "    -> Intentando Scoop..." -ForegroundColor Cyan
            if (!(Get-Command scoop.exe -ErrorAction SilentlyContinue)) {
                Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
                Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression
            }
            & scoop install mpv
            $mpvPath = Find-MpvExe
        }
    }
}

if ($mpvPath) {
    Write-Host "  [OK] MPV: Presente ($mpvPath)" -ForegroundColor Green
    if ($mpvPath -ne "$installDir\mpv.exe" -and (Test-Path $mpvPath)) {
        try {
            $mpvDir = Split-Path $mpvPath -Parent
            Copy-Item -Path "$mpvDir\*" -Destination $installDir -Recurse -Force -ErrorAction SilentlyContinue
        } catch {}
    }
} else {
    Write-Host "  [!] MPV: No se pudo configurar automaticamente." -ForegroundColor Yellow
}

# ------------------------------------------------------------------------------
# 4. Instalacion de BeautifulSoup4 en Python
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
# 5. Descargar la version mas reciente del script principal
# ------------------------------------------------------------------------------
Write-Host ""
Write-Host "[4/5] Descargando Anime-CMD fresco desde el repositorio..." -ForegroundColor Cyan

$cacheBust = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
$repoUrl = "https://raw.githubusercontent.com/HugoAleOlguin/Anime-CMD/main"
$aniScriptUrl = "$repoUrl/ani-es?v=$cacheBust"
$aniScriptPath = "$installDir\ani-es"

try {
    Invoke-WebRequest -Uri $aniScriptUrl -OutFile $aniScriptPath -UseBasicParsing -Headers @{
        "Cache-Control" = "no-cache, no-store, must-revalidate"
        "Pragma"        = "no-cache"
    }
    Write-Host "  [OK] Script principal v2.1 descargado con exito." -ForegroundColor Green
} catch {
    Write-Host "  [!] Reintentando descarga con WebClient..." -ForegroundColor Yellow
    $webClient = New-Object System.Net.WebClient
    $webClient.Headers.Add("Cache-Control", "no-cache, no-store, must-revalidate")
    $webClient.Headers.Add("Pragma", "no-cache")
    $webClient.DownloadFile($aniScriptUrl, $aniScriptPath)
    Write-Host "  [OK] Script principal v2.1 descargado con exito." -ForegroundColor Green
}

# Crear el comando ejecutable anime.cmd
$cmdLines = @(
    "@echo off",
    "setlocal",
    "set `"PATH=%~dp0;%PATH%;%LOCALAPPDATA%\Microsoft\WinGet\Links;%LOCALAPPDATA%\Programs\mpv;C:\Program Files\mpv;C:\Program Files (x86)\mpv;%USERPROFILE%\scoop\shims`"",
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
# 6. Configurar variable de entorno PATH con maxima prioridad
# ------------------------------------------------------------------------------
Write-Host ""
Write-Host "[5/5] Configurando variables de entorno con maxima prioridad..." -ForegroundColor Cyan

$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($null -eq $userPath) { $userPath = "" }

# Extraer y filtrar entradas existentes para evitar duplicados y asegurar prioridad maxima a $installDir
$existingParts = ($userPath -split ';') | Where-Object { $_ -ne "" -and $_.Trim() -ne $installDir }

# Construir lista priorizada: $installDir siempre al principio
$finalPaths = @($installDir)
$wingetLinks = "$env:LOCALAPPDATA\Microsoft\WinGet\Links"
if (Test-Path $wingetLinks) {
    $existingParts = $existingParts | Where-Object { $_.Trim() -ne $wingetLinks }
    $finalPaths += $wingetLinks
}
$scoopShims = "$HOME\scoop\shims"
if (Test-Path $scoopShims) {
    $existingParts = $existingParts | Where-Object { $_.Trim() -ne $scoopShims }
    $finalPaths += $scoopShims
}

$finalPaths += $existingParts
$newUserPath = ($finalPaths -join ';')

[Environment]::SetEnvironmentVariable("Path", $newUserPath, "User")
$env:Path = "$installDir;" + $env:Path

Write-Host "  [OK] $installDir configurado con maxima prioridad en PATH." -ForegroundColor Green

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "  Instalacion limpia de Anime-CMD v2.1 completada!        " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Abre una nueva ventana de terminal (CMD o PowerShell) y ejecuta:" -ForegroundColor Cyan
Write-Host "   anime" -ForegroundColor Yellow
Write-Host ""
