@echo off
cd /d "%~dp0"
if exist "%LOCALAPPDATA%\Attenuation Auditor\attenuation-auditor.exe" (
    start "" "%LOCALAPPDATA%\Attenuation Auditor\attenuation-auditor.exe"
    exit /b 0
)
if exist "src-tauri\target\release\attenuation-auditor.exe" (
    start "" "src-tauri\target\release\attenuation-auditor.exe"
    exit /b 0
)
if exist "src-tauri\target\release\bundle\nsis\Attenuation Auditor_2.0.0_x64-setup.exe" (
    start "" "src-tauri\target\release\bundle\nsis\Attenuation Auditor_2.0.0_x64-setup.exe"
    exit /b 0
)
if exist "releases\Attenuation Auditor_2.0.0_x64-setup.exe" (
    start "" "releases\Attenuation Auditor_2.0.0_x64-setup.exe"
    exit /b 0
)
echo V2 application is not installed or built yet. Run install.bat first.
pause
