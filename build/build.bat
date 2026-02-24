@echo off
REM ============================================================
REM Atomic Downloader - Build Script
REM Creates a single-file Windows EXE
REM ============================================================

echo.
echo  ╔══════════════════════════════════════════════╗
echo  ║     ATOMIC DOWNLOADER - BUILD SYSTEM         ║
echo  ║     Creating Windows EXE...                  ║
echo  ╚══════════════════════════════════════════════╝
echo.

REM Navigate to project root
cd /d "%~dp0\.."

REM Check if PyInstaller is installed
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo [INSTALL] Installing PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo [ERROR] Failed to install PyInstaller!
        pause
        exit /b 1
    )
)

echo [BUILD] Starting PyInstaller build...
echo.

REM Run PyInstaller with the spec file
pyinstaller --clean --noconfirm "build\AtomicDownloader.spec"

if errorlevel 1 (
    echo.
    echo [ERROR] Build failed! Check the errors above.
    pause
    exit /b 1
)

echo.
echo  ╔══════════════════════════════════════════════╗
echo  ║     BUILD SUCCESSFUL!                        ║
echo  ║                                              ║
echo  ║     Output: dist\AtomicDownloader.exe        ║
echo  ║                                              ║
echo  ║     NOTE: Make sure ffmpeg.exe is in the     ║
echo  ║     same folder or in system PATH.           ║
echo  ╚══════════════════════════════════════════════╝
echo.

REM Show file size
for %%I in ("dist\AtomicDownloader.exe") do (
    set SIZE=%%~zI
    echo  File size: %%~zI bytes
)

echo.
pause
