# Instalador de Anime CLI para Windows
$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "       Instalador de Anime CLI            " -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan

$installDir = "$HOME\bin"
if (!(Test-Path $installDir)) {
    New-Item -ItemType Directory -Path $installDir -Force | Out-Null
}

$repoUrl = "https://raw.githubusercontent.com/Zhuchii/ani-es/main"

Write-Host "[1/3] Descargando script principal..." -ForegroundColor Yellow
Invoke-WebRequest -Uri "$repoUrl/ani-es" -OutFile "$installDir\ani-es" -UseBasicParsing

Write-Host "[2/3] Creando ejecutable anime.cmd..." -ForegroundColor Yellow
$cmdContent = @"
@echo off
"C:\Program Files\Git\bin\bash.exe" "$installDir\ani-es" %*
"@
Set-Content -Path "$installDir\anime.cmd" -Value $cmdContent -Encoding ASCII

Write-Host "[3/3] Configurando variables de entorno (PATH)..." -ForegroundColor Yellow
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($userPath -notlike "*$installDir*") {
    [Environment]::SetEnvironmentVariable("Path", "$userPath;$installDir", "User")
    Write-Host "Directorio $installDir agregado al PATH de usuario." -ForegroundColor Green
}

Write-Host ""
Write-Host "¡Instalación completada exitosamente!" -ForegroundColor Green
Write-Host "Abre una nueva ventana de terminal y escribe: anime" -ForegroundColor Cyan
