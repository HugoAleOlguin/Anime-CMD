# ==============================================================================
# Anime-CMD v1.7.0 - Instalador y Actualizador Automatico para Windows
# Repositorio: https://github.com/HugoAleOlguin/Anime-CMD
# ==============================================================================

$ErrorActionPreference = "Continue"
$ProgressPreference = "SilentlyContinue"
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "         Instalador Automatico de Anime-CMD v1.7.0        " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
Write-Host ""

$installDir = "$HOME\.anime"

# ------------------------------------------------------------------------------
# 1. Limpieza de instalaciones anteriores y conflictos
# ------------------------------------------------------------------------------
Write-Host "[1/4] Preparando entorno limpio..." -ForegroundColor Green

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
        } catch {}
    }
}

if (!(Test-Path $installDir)) {
    New-Item -ItemType Directory -Path $installDir -Force | Out-Null
} else {
    Remove-Item -Path "$installDir\ani-es" -Force -ErrorAction SilentlyContinue
    Remove-Item -Path "$installDir\anime.cmd" -Force -ErrorAction SilentlyContinue
    Remove-Item -Path "$installDir\anime.bat" -Force -ErrorAction SilentlyContinue
    Remove-Item -Path "$installDir\ao_eps.json" -Force -ErrorAction SilentlyContinue
    Remove-Item -Path "$installDir\mpv_run.log" -Force -ErrorAction SilentlyContinue
    Remove-Item -Path "$installDir\*.tmp" -Force -ErrorAction SilentlyContinue
}

Write-Host "  [OK] Directorio preparado en $installDir" -ForegroundColor Green

# ------------------------------------------------------------------------------
# 2. Funciones auxiliares de validación
# ------------------------------------------------------------------------------
function Test-ExecutableWorks {
    param([string]$exePath, [string]$testArg = "--version")
    if (!$exePath -or !(Test-Path $exePath)) { return $false }
    try {
        $pinfo = New-Object System.Diagnostics.ProcessStartInfo
        $pinfo.FileName = $exePath
        $pinfo.Arguments = $testArg
        $pinfo.RedirectStandardOutput = $true
        $pinfo.RedirectStandardError = $true
        $pinfo.UseShellExecute = $false
        $pinfo.CreateNoWindow = $true
        $p = [System.Diagnostics.Process]::Start($pinfo)
        $p.WaitForExit(3000)
        if ($p.HasExited -and $p.ExitCode -eq 0) {
            return $true
        }
    } catch {}
    return $false
}

function Resolve-RealExe {
    param([string]$exePath)
    if (!$exePath -or !(Test-Path $exePath)) { return $null }

    $shimFile = [System.IO.Path]::ChangeExtension($exePath, ".shim")
    if (Test-Path $shimFile) {
        try {
            $content = Get-Content $shimFile -Raw
            if ($content -match 'path\s*=\s*"([^"]+)"') {
                $target = $matches[1]
                if (Test-Path $target) { return $target }
            }
        } catch {}
    }

    try {
        $item = Get-Item $exePath -ErrorAction SilentlyContinue
        if ($item -and $item.LinkType -and $item.Target) {
            $target = $item.Target
            if (Test-Path $target) { return $target }
        }
    } catch {}

    return $exePath
}

function Find-MpvExe {
    $searchLocations = @(
        "$installDir\mpv.exe",
        "$HOME\scoop\apps\mpv\current\mpv.exe",
        "$env:USERPROFILE\scoop\apps\mpv\current\mpv.exe",
        "$env:LOCALAPPDATA\Microsoft\WinGet\Links\mpv.exe",
        "$env:LOCALAPPDATA\Programs\mpv\mpv.exe",
        "C:\Program Files\mpv\mpv.exe",
        "C:\Program Files (x86)\mpv\mpv.exe",
        "$HOME\scoop\shims\mpv.exe",
        "C:\ProgramData\chocolatey\bin\mpv.exe"
    )

    if (Get-Command mpv.exe -ErrorAction SilentlyContinue) {
        $searchLocations = @((Get-Command mpv.exe).Source) + $searchLocations
    } elseif (Get-Command mpv -ErrorAction SilentlyContinue) {
        $searchLocations = @((Get-Command mpv).Source) + $searchLocations
    }

    $wingetPkg = "$env:LOCALAPPDATA\Microsoft\WinGet\Packages"
    if (Test-Path $wingetPkg) {
        $found = Get-ChildItem -Path $wingetPkg -Filter "mpv.exe" -Recurse -File -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($found) { $searchLocations += $found.FullName }
    }

    foreach ($loc in $searchLocations) {
        if ($loc -and (Test-Path $loc)) {
            $real = Resolve-RealExe $loc
            if (Test-ExecutableWorks $real) { return $real }
            if (Test-ExecutableWorks $loc) { return $loc }
        }
    }
    return $null
}

function Find-FzfExe {
    $searchLocations = @(
        "$installDir\fzf.exe",
        "$HOME\scoop\apps\fzf\current\fzf.exe",
        "$env:USERPROFILE\scoop\apps\fzf\current\fzf.exe",
        "$env:LOCALAPPDATA\Microsoft\WinGet\Links\fzf.exe",
        "$HOME\scoop\shims\fzf.exe",
        "C:\ProgramData\chocolatey\bin\fzf.exe"
    )

    if (Get-Command fzf.exe -ErrorAction SilentlyContinue) {
        $searchLocations = @((Get-Command fzf.exe).Source) + $searchLocations
    } elseif (Get-Command fzf -ErrorAction SilentlyContinue) {
        $searchLocations = @((Get-Command fzf).Source) + $searchLocations
    }

    $wingetPkg = "$env:LOCALAPPDATA\Microsoft\WinGet\Packages"
    if (Test-Path $wingetPkg) {
        $found = Get-ChildItem -Path $wingetPkg -Filter "fzf.exe" -Recurse -File -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($found) { $searchLocations += $found.FullName }
    }

    foreach ($loc in $searchLocations) {
        if ($loc -and (Test-Path $loc)) {
            $real = Resolve-RealExe $loc
            if (Test-ExecutableWorks $real) { return $real }
            if (Test-ExecutableWorks $loc) { return $loc }
        }
    }
    return $null
}

# ------------------------------------------------------------------------------
# 3. Obtener Anime-CMD (Prioridad: Binario nativo standalone sin dependencias)
# ------------------------------------------------------------------------------
Write-Host ""
Write-Host "[2/4] Configurando Anime-CMD v1.7.0..." -ForegroundColor Green

$isStandalone = $false
$hasLocalSource = $false
$localRoot = $null

if (![string]::IsNullOrEmpty($PSScriptRoot) -and (Test-Path "$PSScriptRoot\src\main.py")) {
    $localRoot = $PSScriptRoot
    $hasLocalSource = $true
} elseif (Test-Path ".\src\main.py") {
    $localRoot = (Get-Location).Path
    $hasLocalSource = $true
}

# Caso 1: Instalación local
if ($hasLocalSource) {
    Copy-Item -Path "$localRoot\src" -Destination $installDir -Recurse -Force -ErrorAction SilentlyContinue
    if (Test-Path "$localRoot\dist\anime.exe") {
        Copy-Item -Path "$localRoot\dist\anime.exe" -Destination "$installDir\anime.exe" -Force -ErrorAction SilentlyContinue
        $isStandalone = $true
        Write-Host "  [OK] Binario nativo anime.exe instalado desde compilacion local." -ForegroundColor Green
    } elseif (Test-Path "$localRoot\anime.exe") {
        Copy-Item -Path "$localRoot\anime.exe" -Destination "$installDir\anime.exe" -Force -ErrorAction SilentlyContinue
        $isStandalone = $true
        Write-Host "  [OK] Binario nativo anime.exe instalado." -ForegroundColor Green
    } else {
        Write-Host "  [OK] Codigo fuente local src/ copiado a $installDir" -ForegroundColor Green
    }
} else {
    # Caso 2: Instalación remota via web (irm ... | iex)
    Write-Host "  [*] Descargando ejecutable standalone (no requiere Python ni Git)..." -ForegroundColor Cyan
    $releaseExeUrl = "https://github.com/HugoAleOlguin/Anime-CMD/releases/latest/download/anime.exe"
    try {
        Invoke-WebRequest -Uri $releaseExeUrl -OutFile "$installDir\anime.exe" -UseBasicParsing -TimeoutSec 45
        if ((Test-Path "$installDir\anime.exe") -and (Get-Item "$installDir\anime.exe").Length -gt 5000000) {
            $isStandalone = $true
            Write-Host "  [OK] Binario standalone anime.exe descargado con exito." -ForegroundColor Green
        } else {
            Remove-Item -Path "$installDir\anime.exe" -Force -ErrorAction SilentlyContinue
        }
    } catch {
        Remove-Item -Path "$installDir\anime.exe" -Force -ErrorAction SilentlyContinue
    }

    # Si no se pudo bajar el binario (fallback a código fuente)
    if (!$isStandalone) {
        Write-Host "  [!] Descargando codigo fuente como fallback..." -ForegroundColor Yellow
        $zipPath = "$env:TEMP\anime_repo.zip"
        $extractDir = "$env:TEMP\anime_extracted"
        try {
            Remove-Item -Path $zipPath -Force -ErrorAction SilentlyContinue
            Remove-Item -Path $extractDir -Recurse -Force -ErrorAction SilentlyContinue
            Invoke-WebRequest -Uri "https://github.com/HugoAleOlguin/Anime-CMD/archive/refs/heads/main.zip" -OutFile $zipPath -UseBasicParsing
            Expand-Archive -Path $zipPath -DestinationPath $extractDir -Force
            $extractedSrc = Get-ChildItem -Path $extractDir -Recurse -Filter "src" -Directory | Select-Object -First 1
            if ($extractedSrc -and (Test-Path $extractedSrc.FullName)) {
                Copy-Item -Path $extractedSrc.FullName -Destination $installDir -Recurse -Force
                Write-Host "  [OK] Codigo fuente descargado e instalado en $installDir" -ForegroundColor Green
            }
        } catch {
            Write-Host "  [!] Error descargando codigo fuente: $_" -ForegroundColor Red
        } finally {
            Remove-Item -Path $zipPath -Force -ErrorAction SilentlyContinue
            Remove-Item -Path $extractDir -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
}

# ------------------------------------------------------------------------------
# 4. Verificacion de componentes (FZF y MPV Player)
# ------------------------------------------------------------------------------
Write-Host ""
Write-Host "[3/4] Verificando componentes multimedia (FZF y MPV)..." -ForegroundColor Green

# FZF
$fzfPath = Find-FzfExe
if (!$fzfPath) {
    Write-Host "  [*] Descargando FZF..." -ForegroundColor Green
    try {
        $fzfZip = "$env:TEMP\fzf_download.zip"
        Invoke-WebRequest -Uri "https://github.com/junegunn/fzf/releases/download/v0.60.3/fzf-0.60.3-windows_amd64.zip" -OutFile $fzfZip -UseBasicParsing
        Expand-Archive -Path $fzfZip -DestinationPath $installDir -Force
        Remove-Item -Path $fzfZip -Force -ErrorAction SilentlyContinue
        if (Test-ExecutableWorks "$installDir\fzf.exe") {
            $fzfPath = "$installDir\fzf.exe"
        }
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
            $realFzf = Resolve-RealExe $fzfPath
            if (Test-ExecutableWorks $realFzf) {
                Copy-Item -Path $realFzf -Destination "$installDir\fzf.exe" -Force -ErrorAction SilentlyContinue
            }
        } catch {}
    }
} else {
    Write-Host "  [!] FZF: Opcional, navegacion estandar activada." -ForegroundColor Yellow
}

# MPV Player
$mpvPath = Find-MpvExe
if (!$mpvPath) {
    Write-Host "  [*] Configurando reproductor MPV optimizado..." -ForegroundColor Green
    try {
        $mpv7z = "$env:TEMP\mpv_download.7z"
        Write-Host "    -> Descargando reproductor portatil..." -ForegroundColor Green
        Invoke-WebRequest -Uri "https://github.com/shinchiro/mpv-winbuild-cmake/releases/download/20260814/mpv-x86_64-20260814-git-7b8915bc1d.7z" -OutFile $mpv7z -UseBasicParsing
        & tar -xf $mpv7z -C $installDir
        Remove-Item -Path $mpv7z -Force -ErrorAction SilentlyContinue
        if (Test-ExecutableWorks "$installDir\mpv.exe") {
            $mpvPath = "$installDir\mpv.exe"
        }
    } catch {
        if (Get-Command winget.exe -ErrorAction SilentlyContinue) {
            & winget install --id shinchiro.mpv -e --source winget --accept-package-agreements --accept-source-agreements --silent
            $mpvPath = Find-MpvExe
        }
    }
}

if ($mpvPath) {
    Write-Host "  [OK] MPV Player: Presente ($mpvPath)" -ForegroundColor Green
    if ($mpvPath -ne "$installDir\mpv.exe" -and (Test-Path $mpvPath)) {
        try {
            $realMpv = Resolve-RealExe $mpvPath
            if (Test-ExecutableWorks $realMpv) {
                $mpvDir = Split-Path $realMpv -Parent
                if ($mpvDir -notmatch 'shims' -and $mpvDir -ne $installDir) {
                    Copy-Item -Path "$mpvDir\*" -Destination $installDir -Recurse -Force -ErrorAction SilentlyContinue
                } else {
                    Copy-Item -Path $realMpv -Destination "$installDir\mpv.exe" -Force -ErrorAction SilentlyContinue
                }
            }
        } catch {}
    }
} else {
    Write-Host "  [!] MPV: Se recomienda instalar MPV para la reproduccion." -ForegroundColor Yellow
}

# Solo si NO se tiene el binario standalone, se configuran las dependencias de Python
if (!$isStandalone -and (Test-Path "$installDir\src\main.py")) {
    Write-Host ""
    Write-Host "  [*] Modo codigo fuente: verificando entorno Python..." -ForegroundColor Cyan
    $hasPython = (Get-Command python.exe -ErrorAction SilentlyContinue) -or `
                 (Get-Command python3.exe -ErrorAction SilentlyContinue) -or `
                 (Get-Command py.exe -ErrorAction SilentlyContinue)
    if (!$hasPython -and (Get-Command winget.exe -ErrorAction SilentlyContinue)) {
        & winget install --id Python.Python.3.12 -e --source winget --accept-package-agreements --accept-source-agreements --silent
    }
    if (Get-Command pip -ErrorAction SilentlyContinue) {
        & pip install --quiet beautifulsoup4 curl_cffi 2>&1 | Out-Null
    }
}

# ------------------------------------------------------------------------------
# 5. Generar lanzador anime.cmd y configurar variable de entorno PATH
# ------------------------------------------------------------------------------
Write-Host ""
Write-Host "[4/4] Configurando variables de entorno con maxima prioridad..." -ForegroundColor Green

$cmdLines = @(
    "@echo off",
    "setlocal",
    "set `"PATH=%~dp0;%PATH%;%LOCALAPPDATA%\Microsoft\WinGet\Links;%LOCALAPPDATA%\Programs\mpv;C:\Program Files\mpv;C:\Program Files (x86)\mpv;%USERPROFILE%\scoop\shims;%USERPROFILE%\scoop\apps\fzf\current;%USERPROFILE%\scoop\apps\mpv\current`"",
    "",
    "if exist `"%~dp0anime.exe`" (",
    "    `"%~dp0anime.exe`" %*",
    "    exit /b %ERRORLEVEL%",
    ")",
    "",
    "if exist `"%~dp0src\main.py`" (",
    "    python `"%~dp0src\main.py`" %*",
    "    exit /b %ERRORLEVEL%",
    ")",
    "",
    "echo [ERROR] No se encontro anime.exe ni el codigo fuente en %~dp0",
    "echo Por favor ejecuta de nuevo el instalador de Anime-CMD.",
    "exit /b 1"
)

[System.IO.File]::WriteAllLines("$installDir\anime.cmd", $cmdLines)
Write-Host "  [OK] Lanzador universal anime.cmd generado." -ForegroundColor Green

$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($null -eq $userPath) { $userPath = "" }

$existingParts = ($userPath -split ';') | Where-Object { $_ -ne "" -and $_.Trim() -ne $installDir }
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
$scoopAppsFzf = "$HOME\scoop\apps\fzf\current"
if (Test-Path $scoopAppsFzf) {
    $existingParts = $existingParts | Where-Object { $_.Trim() -ne $scoopAppsFzf }
    $finalPaths += $scoopAppsFzf
}

$finalPaths += $existingParts
$newCombinedPath = ($finalPaths | Where-Object { $_ -ne "" }) -join ';'

[Environment]::SetEnvironmentVariable("Path", $newCombinedPath, "User")
$env:Path = "$installDir;$env:Path"

Write-Host "  [OK] $installDir configurado con maxima prioridad en PATH." -ForegroundColor Green

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "  Instalacion limpia de Anime-CMD v1.7.0 completada!      " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Abre una nueva ventana de terminal (CMD o PowerShell) y ejecuta:" -ForegroundColor Green
Write-Host "   anime" -ForegroundColor Yellow
Write-Host ""
