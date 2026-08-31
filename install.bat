@echo off
setlocal
cd /d "%~dp0"

set "SETUP_PATH=releases\Attenuation Auditor_2.0.0_x64-setup.exe"
if not exist "%SETUP_PATH%" set "SETUP_PATH=src-tauri\target\release\bundle\nsis\Attenuation Auditor_2.0.0_x64-setup.exe"
if not exist "%SETUP_PATH%" (
    echo [Attenuation Auditor] No V2 installer found. Building it first...
    call build_v2.bat
    if errorlevel 1 exit /b 1
    set "SETUP_PATH=src-tauri\target\release\bundle\nsis\Attenuation Auditor_2.0.0_x64-setup.exe"
)

if exist "att_auditor_exceptions.json" (
    if not exist "%APPDATA%\com.attenuationauditor.desktop" mkdir "%APPDATA%\com.attenuationauditor.desktop"
    if not exist "%APPDATA%\com.attenuationauditor.desktop\att_auditor_exceptions.json" copy /Y "att_auditor_exceptions.json" "%APPDATA%\com.attenuationauditor.desktop\att_auditor_exceptions.json" >nul
)

echo [Attenuation Auditor] Starting V2 installer...
start "" /wait "%SETUP_PATH%"
echo.
echo [DONE] Installation step finished.
echo Optional: run install_addon.bat to register the Wwise Tools menu command.
pause
