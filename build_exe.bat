@echo off
chcp 65001 >nul
REM Quick build script - using spec file
echo ====================================
echo LOL Data Collector - Quick Build
echo ====================================
echo.

cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python not found in PATH
    pause
    exit /b 1
)

REM Check if PyInstaller is installed
python -c "import PyInstaller" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing PyInstaller...
    pip install pyinstaller
)

REM Clean previous build results
if exist "dist" rmdir /s /q "dist"
if exist "build\output" rmdir /s /q "build\output"

REM Build using spec file
echo Building executable using spec file...
python -m PyInstaller --clean --workpath build\output build\LoLDataCollector.spec

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo Build completed successfully!
    echo Executable location: dist\LoLDataCollector.exe
    echo ========================================
    if exist "dist\LoLDataCollector.exe" (
        echo File size: 
        dir "dist\LoLDataCollector.exe" | find ".exe"
    )
) else (
    echo.
    echo ========================================
    echo Build failed with error code: %errorlevel%
    echo ========================================
)

echo.
pause
