@echo off
cd /d "%~dp0"
if not exist "dist\SDown.exe" (
    echo SDown.exe bulunamadi. Once .\build.ps1 komutuyla derleyin.
    pause
    exit /b 1
)
start "" "%~dp0dist\SDown.exe"
