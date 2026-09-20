@echo off
chcp 65001 >nul
title 6698 KVKK Başvuru Portalı - Kolay Başlatıcı
cd /d "%~dp0"

echo ======================================================================
echo    🛡️ 6698 KVKK İlgili Kişi Başvuru Portalı - Başlatıcı
echo ======================================================================
echo.

where python >nul 2>nul
if %errorlevel% equ 0 (
    start http://localhost:8080/
    python server.py
    goto :end
)

if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    start http://localhost:8080/
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" server.py
    goto :end
)

echo [BİLGİ] Python bulunamadı. Form doğrudan tarayıcınızda açılıyor...
timeout /t 1 >nul
start "" "%~dp0index.html"

:end
