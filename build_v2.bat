@echo off
setlocal
cd /d "%~dp0"

where npm >nul 2>&1 || (echo [ERROR] Node.js/npm is required. & exit /b 1)
where cargo >nul 2>&1 || (echo [ERROR] Rust/cargo is required. & exit /b 1)

set "PYTHON_EXE="
for /f "delims=" %%P in ('where python 2^>nul') do if not defined PYTHON_EXE set "PYTHON_EXE=%%P"
if not defined PYTHON_EXE (echo [ERROR] Python 3.10+ is required. & exit /b 1)

if not exist ".venv\Scripts\python.exe" "%PYTHON_EXE%" -m venv .venv
if errorlevel 1 exit /b 1

echo [1/4] Installing Python backend dependencies...
.venv\Scripts\python.exe -m pip install --upgrade waapi-client pyinstaller
if errorlevel 1 exit /b 1

echo [2/4] Installing frontend dependencies...
call npm install
if errorlevel 1 exit /b 1

echo [3/4] Packaging WAAPI backend...
if not exist "src-tauri\resources" mkdir "src-tauri\resources"
.venv\Scripts\pyinstaller.exe --noconfirm --clean --onefile --name auditor_backend --distpath src-tauri\resources --workpath build\auditor_backend --specpath build --icon "%CD%\assets\icon.ico" auditor_backend.py
if errorlevel 1 exit /b 1

echo [4/4] Building Tauri application and NSIS installer...
call npm run tauri -- build
if errorlevel 1 exit /b 1

echo.
echo [DONE] src-tauri\target\release\bundle\nsis\Attenuation Auditor_2.0.0_x64-setup.exe
