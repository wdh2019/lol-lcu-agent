@echo off
echo ====================================
echo LOL Game Data Collector - Simple Build Script
echo ====================================
echo.

cd /d "%~dp0"
cd ..

echo Using absolute paths...
echo Current directory: %cd%

echo Generating the executable using PyInstaller...
python -m PyInstaller --clean --onefile --windowed --name LoLDataCollector --icon=%cd%\resources\icon.ico %cd%\main.py

echo.
if %errorlevel% equ 0 (
    echo Build completed successfully!
    echo The executable is located in the 'dist' directory.
) else (
    echo Build failed!
)

pause
