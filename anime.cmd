@echo off
setlocal
set "PATH=%~dp0;%PATH%;%LOCALAPPDATA%\Microsoft\WinGet\Links;%LOCALAPPDATA%\Programs\mpv;C:\Program Files\mpv;C:\Program Files (x86)\mpv;%USERPROFILE%\scoop\shims;%USERPROFILE%\scoop\apps\fzf\current;%USERPROFILE%\scoop\apps\mpv\current"

if exist "%~dp0anime.exe" (
    "%~dp0anime.exe" %*
    exit /b %ERRORLEVEL%
)

if exist "%~dp0dist\anime.exe" (
    "%~dp0dist\anime.exe" %*
    exit /b %ERRORLEVEL%
)

if exist "%~dp0src\main.py" (
    python "%~dp0src\main.py" %*
    exit /b %ERRORLEVEL%
)

set "BASH_PATH="
if exist "C:\Program Files\Git\bin\bash.exe" (
    set "BASH_PATH=C:\Program Files\Git\bin\bash.exe"
) else if exist "%LOCALAPPDATA%\Programs\Git\bin\bash.exe" (
    set "BASH_PATH=%LOCALAPPDATA%\Programs\Git\bin\bash.exe"
) else (
    for %%X in (bash.exe) do (set "BASH_PATH=%%~$PATH:X")
)

if defined BASH_PATH (
    if exist "%~dp0ani-es" (
        "%BASH_PATH%" "%~dp0ani-es" %*
        exit /b %ERRORLEVEL%
    )
)

echo [ERROR] No se encontro anime.exe, Python ni Git Bash para ejecutar Anime-CMD.
exit /b 1
