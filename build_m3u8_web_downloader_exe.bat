@echo off
setlocal

REM Build one-file EXE for m3u8_web_downloader.py
REM Usage: run this file in Windows CMD from repo root.

where py >nul 2>nul
if %ERRORLEVEL% neq 0 (
  echo [ERROR] Python launcher ^(py^) not found. Please install Python 3 first.
  exit /b 1
)

echo [INFO] Installing/Updating PyInstaller...
py -3 -m pip install --upgrade pyinstaller
if %ERRORLEVEL% neq 0 (
  echo [ERROR] Failed to install PyInstaller.
  exit /b 1
)

echo [INFO] Building EXE...
py -3 -m PyInstaller --clean --noconfirm --onefile --name m3u8_web_downloader m3u8_web_downloader.py
if %ERRORLEVEL% neq 0 (
  echo [ERROR] Build failed.
  exit /b 1
)

echo [DONE] Build succeeded.
echo [INFO] Output: dist\m3u8_web_downloader.exe
endlocal
