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
Write-Host "[1/5] Limpiando versiones y archivos temporales anteriores..." -ForegroundColor Green

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
    Remove-Item -Path "$installDir\ao_eps.json" -Force -ErrorAction SilentlyContinue
    Remove-Item -Path "$installDir\mpv_run.log" -Force -ErrorAction SilentlyContinue
    Remove-Item -Path "$installDir\*.tmp" -Force -ErrorAction SilentlyContinue
}

Write-Host "  [OK] Entorno limpio preparado en $installDir" -ForegroundColor Green

# ------------------------------------------------------------------------------
# 2. Funciones auxiliares de validación y localización de ejecutables
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

    # 1. Si es un shim de Scoop (existe un archivo .shim hermano)
    $shimFile = [System.IO.Path]::ChangeExtension($exePath, ".shim")
    if (Test-Path $shimFile) {
        try {
            $content = Get-Content $shimFile -Raw
            if ($content -match 'path\s*=\s*"([^"]+)"') {
                $target = $matches[1]
                if (Test-Path $target) {
                    return $target
                }
            }
        } catch {}
    }

    # 2. Si es un enlace simbólico o junction
    try {
        $item = Get-Item $exePath -ErrorAction SilentlyContinue
        if ($item -and $item.LinkType -and $item.Target) {
            $target = $item.Target
            if (Test-Path $target) {
                return $target
            }
        }
    } catch {}

    return $exePath
}

# Limpieza preventiva de binarios corruptos o shims huérfanos en $installDir
if (Test-Path "$installDir\fzf.exe") {
    if (!(Test-ExecutableWorks "$installDir\fzf.exe")) {
        Remove-Item -Path "$installDir\fzf.exe" -Force -ErrorAction SilentlyContinue
        Write-Host "  -> Shim/ejecutable fzf.exe inválido eliminado de $installDir" -ForegroundColor Gray
    }
}
if (Test-Path "$installDir\mpv.exe") {
    if (!(Test-ExecutableWorks "$installDir\mpv.exe")) {
        Remove-Item -Path "$installDir\mpv.exe" -Force -ErrorAction SilentlyContinue
        Write-Host "  -> Shim/ejecutable mpv.exe inválido eliminado de $installDir" -ForegroundColor Gray
    }
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
        if ($found) {
            $searchLocations += $found.FullName
        }
    }

    foreach ($loc in $searchLocations) {
        if ($loc -and (Test-Path $loc)) {
            $real = Resolve-RealExe $loc
            if (Test-ExecutableWorks $real) {
                return $real
            }
            if (Test-ExecutableWorks $loc) {
                return $loc
            }
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
        if ($found) {
            $searchLocations += $found.FullName
        }
    }

    foreach ($loc in $searchLocations) {
        if ($loc -and (Test-Path $loc)) {
            $real = Resolve-RealExe $loc
            if (Test-ExecutableWorks $real) {
                return $real
            }
            if (Test-ExecutableWorks $loc) {
                return $loc
            }
        }
    }

    return $null
}

# ------------------------------------------------------------------------------
# 3. Verificacion e instalacion de dependencias necesarias
# ------------------------------------------------------------------------------
Write-Host ""
Write-Host "[2/5] Verificando dependencias esenciales..." -ForegroundColor Green

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
    Write-Host "  [*] Instalando FZF de forma autonoma..." -ForegroundColor Green
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
    Write-Host "  [!] FZF: No se pudo configurar automaticamente." -ForegroundColor Yellow
}

# MPV
$mpvPath = Find-MpvExe
if (!$mpvPath) {
    Write-Host "  [*] Instalando MPV Player de forma autonoma..." -ForegroundColor Green
    
    # 1. Descarga directa standalone de MPV
    try {
        $mpv7z = "$env:TEMP\mpv_download.7z"
        Write-Host "    -> Descargando paquete optimizado de MPV..." -ForegroundColor Green
        Invoke-WebRequest -Uri "https://github.com/shinchiro/mpv-winbuild-cmake/releases/download/20260814/mpv-x86_64-20260814-git-7b8915bc1d.7z" -OutFile $mpv7z -UseBasicParsing
        & tar -xf $mpv7z -C $installDir
        Remove-Item -Path $mpv7z -Force -ErrorAction SilentlyContinue
        if (Test-ExecutableWorks "$installDir\mpv.exe") {
            $mpvPath = "$installDir\mpv.exe"
        }
    } catch {
        # Fallback a WinGet o Scoop si la descarga directa fallara
        if (Get-Command winget.exe -ErrorAction SilentlyContinue) {
            Write-Host "    -> Intentando WinGet..." -ForegroundColor Green
            & winget install --id shinchiro.mpv -e --source winget --accept-package-agreements --accept-source-agreements --silent
            $mpvPath = Find-MpvExe
        }
        if (!$mpvPath) {
            Write-Host "    -> Intentando Scoop..." -ForegroundColor Green
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
    Write-Host "  [!] MPV: No se pudo configurar automaticamente." -ForegroundColor Yellow
}

# ------------------------------------------------------------------------------
# 4. Instalacion de BeautifulSoup4 y curl_cffi en Python
# ------------------------------------------------------------------------------
Write-Host ""
Write-Host "[3/5] Configurando librerias de Python..." -ForegroundColor Green

if (Get-Command pip -ErrorAction SilentlyContinue) {
    & pip install --quiet beautifulsoup4 curl_cffi 2>&1 | Out-Null
    Write-Host "  [OK] BeautifulSoup4 y curl_cffi configurados correctamente." -ForegroundColor Green
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    & py -m pip install --quiet beautifulsoup4 curl_cffi 2>&1 | Out-Null
    Write-Host "  [OK] BeautifulSoup4 y curl_cffi configurados correctamente." -ForegroundColor Green
}

# ------------------------------------------------------------------------------
# 5. Instalar codigo fuente y lanzador de Anime-CMD v1.7.0
# ------------------------------------------------------------------------------
Write-Host ""
Write-Host "[4/5] Configurando Anime-CMD v1.7.0..." -ForegroundColor Green

# Caso A: Instalación local desde repositorio clonado
$localSrc = Join-Path $PSScriptRoot "src"
$localDistExe = Join-Path $PSScriptRoot "dist\anime.exe"
$localRootExe = Join-Path $PSScriptRoot "anime.exe"

if (Test-Path $localSrc) {
    Copy-Item -Path $localSrc -Destination $installDir -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "  [OK] Codigo fuente src/ copiado a $installDir" -ForegroundColor Green
    if (Test-Path $localDistExe) {
        Copy-Item -Path $localDistExe -Destination "$installDir\anime.exe" -Force -ErrorAction SilentlyContinue
        Write-Host "  [OK] Binario nativo anime.exe instalado." -ForegroundColor Green
    } elseif (Test-Path $localRootExe) {
        Copy-Item -Path $localRootExe -Destination "$installDir\anime.exe" -Force -ErrorAction SilentlyContinue
        Write-Host "  [OK] Binario nativo anime.exe instalado." -ForegroundColor Green
    }
} else {
    # Caso B: Instalación remota via web (irm ... | iex)
    $releaseExeUrl = "https://github.com/HugoAleOlguin/Anime-CMD/releases/latest/download/anime.exe"
    $downloadedExe = $false
    try {
        Invoke-WebRequest -Uri $releaseExeUrl -OutFile "$installDir\anime.exe" -UseBasicParsing -TimeoutSec 15
        if ((Test-Path "$installDir\anime.exe") -and (Get-Item "$installDir\anime.exe").Length -gt 1000000) {
            $downloadedExe = $true
            Write-Host "  [OK] Binario standalone anime.exe descargado desde Releases." -ForegroundColor Green
        }
    } catch {}

    if (!$downloadedExe) {
        $cloneDir = "$installDir\repo"
        if (Get-Command git.exe -ErrorAction SilentlyContinue) {
            if (Test-Path $cloneDir) {
                try { (Push-Location $cloneDir); git pull --quiet; (Pop-Location) } catch {}
            } else {
                git clone --depth 1 --quiet "https://github.com/HugoAleOlguin/Anime-CMD.git" $cloneDir 2>$null
            }
        }
        if (Test-Path "$cloneDir\src") {
            Copy-Item -Path "$cloneDir\src" -Destination $installDir -Recurse -Force -ErrorAction SilentlyContinue
            Write-Host "  [OK] Codigo fuente clonado e instalado en $installDir" -ForegroundColor Green
        } else {
            $zipPath = "$env:TEMP\anime_repo.zip"
            try {
                Invoke-WebRequest -Uri "https://github.com/HugoAleOlguin/Anime-CMD/archive/refs/heads/main.zip" -OutFile $zipPath -UseBasicParsing
                Expand-Archive -Path $zipPath -DestinationPath "$env:TEMP\anime_extracted" -Force
                if (Test-Path "$env:TEMP\anime_extracted\Anime-CMD-main\src") {
                    Copy-Item -Path "$env:TEMP\anime_extracted\Anime-CMD-main\src" -Destination $installDir -Recurse -Force
                    Write-Host "  [OK] Codigo fuente descargado e instalado en $installDir" -ForegroundColor Green
                }
            } catch {} finally {
                Remove-Item -Path $zipPath -Force -ErrorAction SilentlyContinue
                Remove-Item -Path "$env:TEMP\anime_extracted" -Recurse -Force -ErrorAction SilentlyContinue
            }
        }
    }
}

# Crear el comando ejecutable universal anime.cmd
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
    "for %%X in (python.exe) do (",
    "    if exist `"%%~`$PATH:X`" (",
    "        `"%%~`$PATH:X`" `"%~dp0src\main.py`" %*",
    "        exit /b %ERRORLEVEL%",
    "    )",
    ")",
    "",
    "echo [ERROR] No se encontro anime.exe ni Python para ejecutar Anime-CMD.",
    "exit /b 1"
)

[System.IO.File]::WriteAllLines("$installDir\anime.cmd", $cmdLines)
Write-Host "  [OK] Lanzador universal anime.cmd generado." -ForegroundColor Green

# ------------------------------------------------------------------------------
# 6. Configurar variable de entorno PATH con maxima prioridad
# ------------------------------------------------------------------------------
Write-Host ""
Write-Host "[5/5] Configurando variables de entorno con maxima prioridad..." -ForegroundColor Green

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
$scoopAppsFzf = "$HOME\scoop\apps\fzf\current"
if (Test-Path $scoopAppsFzf) {
    $existingParts = $existingParts | Where-Object { $_.Trim() -ne $scoopAppsFzf }
    $finalPaths += $scoopAppsFzf
}

$finalPaths += $existingParts
$newUserPath = ($finalPaths -join ';')

[Environment]::SetEnvironmentVariable("Path", $newUserPath, "User")
$env:Path = "$installDir;" + $env:Path

Write-Host "  [OK] $installDir configurado con maxima prioridad en PATH." -ForegroundColor Green

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "  Instalacion limpia de Anime-CMD v1.7.0 completada!      " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Abre una nueva ventana de terminal (CMD o PowerShell) y ejecuta:" -ForegroundColor Green
Write-Host "   anime" -ForegroundColor Yellow
Write-Host ""
