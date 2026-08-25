@echo off
setlocal
set "BASH_PATH="

if exist "C:\Program Files\Git\bin\bash.exe" (
    set "BASH_PATH=C:\Program Files\Git\bin\bash.exe"
) else if exist "%LOCALAPPDATA%\Programs\Git\bin\bash.exe" (
    set "BASH_PATH=%LOCALAPPDATA%\Programs\Git\bin\bash.exe"
) else (
    for %%X in (bash.exe) do (set "BASH_PATH=%%~$PATH:X")
)

if not defined BASH_PATH (
    echo [ERROR] Git Bash no fue encontrado. Asegurate de tener Git instalado.
    exit /b 1
)

"%BASH_PATH%" "%~dp0ani-es" %*
