@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"

set "LAUNCH_PATH=%LOCALAPPDATA%\Attenuation Auditor\attenuation-auditor.exe"
if not exist "%LAUNCH_PATH%" set "LAUNCH_PATH=%~dp0src-tauri\target\release\attenuation-auditor.exe"
if not exist "%LAUNCH_PATH%" set "LAUNCH_PATH=%~dp0launch.bat"
set "ADDON_DIR=%APPDATA%\Audiokinetic\Wwise\Add-ons\Commands"

if not exist "%ADDON_DIR%" mkdir "%ADDON_DIR%"

powershell -NoProfile -Command "$launch = '%LAUNCH_PATH%'; $json = ConvertTo-Json @{version=1; commands=@(@{id='com.tools.attenuation-auditor'; displayName='Attenuation Auditor'; program=$launch; mainMenu=@{basePath='Tools'}})} -Depth 5; Set-Content -Path '%ADDON_DIR%\AttenuationAuditor.json' -Value $json -Encoding UTF8"

if errorlevel 1 (
    echo [ERROR] Add-on file creation failed.
    pause
    exit /b 1
)

echo.
echo [DONE] Wwise Add-on registered:
echo   %ADDON_DIR%\AttenuationAuditor.json
echo.
echo If Wwise is running: Tools ^> Reload Command Add-ons
echo Otherwise restart Wwise to see "Attenuation Auditor" in the Tools menu.
echo.
pause
