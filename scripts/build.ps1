# Script de compilación local para Windows
$ErrorActionPreference = "Stop"
Write-Host "Compilando Anime-CMD a binario autonomo anime.exe..." -ForegroundColor Green

python -m PyInstaller --clean --noconfirm build/anime.spec

if (Test-Path "dist/anime.exe") {
    Write-Host "[OK] Compilacion completada con exito en dist/anime.exe" -ForegroundColor Green
} else {
    Write-Host "[ERROR] No se encontro dist/anime.exe" -ForegroundColor Red
    exit 1
}
