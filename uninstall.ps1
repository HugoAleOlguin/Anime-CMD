<#
==============================================================================
Anime-CMD - Desinstalador Limpio para Windows
==============================================================================
Elimina por completo la instalación local de Anime-CMD, sus configuraciones,
bases de datos, ejecutables y la entrada del PATH en el sistema.
#>

$ProgressPreference = "SilentlyContinue"
$ErrorActionPreference = "Continue"

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Red
Write-Host "          Desinstalador de Anime-CMD (Windows)            " -ForegroundColor Red
Write-Host "==========================================================" -ForegroundColor Red
Write-Host ""

# 1. Detener procesos activos
Write-Host "[1/3] Cerrando procesos en ejecucion (anime, mpv)..." -ForegroundColor Yellow
try {
    Get-Process anime, mpv -ErrorAction SilentlyContinue | Stop-Process -Force
    Write-Host "  [OK] Procesos detenidos." -ForegroundColor Green
} catch {
    Write-Host "  [i] No habia procesos activos." -ForegroundColor DarkGray
}

# 2. Eliminar directorios de instalacion
Write-Host ""
Write-Host "[2/3] Borrando carpetas y archivos locales..." -ForegroundColor Yellow
$pathsToDelete = @(
    "$HOME\.anime",
    "$HOME\ani-es",
    "$HOME\.anime-cmd"
)

foreach ($p in $pathsToDelete) {
    if (Test-Path $p) {
        try {
            Remove-Item -Path $p -Recurse -Force -ErrorAction Stop
            Write-Host "  [OK] Eliminado: $p" -ForegroundColor Green
        } catch {
            Write-Host "  [!] No se pudo eliminar completamente: $p" -ForegroundColor DarkYellow
        }
    }
}

# 3. Limpiar PATH del usuario
Write-Host ""
Write-Host "[3/3] Limpiando la variable PATH del usuario..." -ForegroundColor Yellow
try {
    $userPath = [Environment]::GetEnvironmentVariable("Path", "User")
    if ($userPath) {
        $cleanDirs = $userPath -split ';' | Where-Object {
            $_ -and $_ -ne "$HOME\.anime" -and $_ -ne "$env:USERPROFILE\.anime"
        }
        $newPath = $cleanDirs -join ';'
        [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
        $env:Path = ($env:Path -split ';' | Where-Object {
            $_ -and $_ -ne "$HOME\.anime" -and $_ -ne "$env:USERPROFILE\.anime"
        }) -join ';'
        Write-Host "  [OK] PATH actualizado en el registro." -ForegroundColor Green
    }
} catch {
    Write-Host "  [!] Error al actualizar PATH en el registro: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "  ✨ Anime-CMD ha sido desinstalado por completo ✨        " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
Write-Host ""
