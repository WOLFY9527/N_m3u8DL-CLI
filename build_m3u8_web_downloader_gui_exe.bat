@echo off
setlocal

REM Build one-file GUI EXE for m3u8_web_downloader_gui.py
REM Usage: run this in Windows CMD from repo root.

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

echo [INFO] Building GUI EXE...
py -3 -m PyInstaller --clean --noconfirm --onefile --windowed --name m3u8_web_downloader_gui m3u8_web_downloader_gui.py
if %ERRORLEVEL% neq 0 (
  echo [ERROR] Build failed.
  exit /b 1
)

echo [DONE] Build succeeded.
echo [INFO] Output: dist\m3u8_web_downloader_gui.exe
endlocal
