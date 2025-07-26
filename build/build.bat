@echo off
echo ====================================
echo LOL Game Data Collector - Build Script
echo ====================================
echo.

cd /d "%~dp0"
cd ..

echo Using absolute paths...
echo Current directory: %cd%

echo Checking if spec file exists...
if exist "build\LoLDataCollector.spec" (
    echo Using existing spec file for build...
    python -m PyInstaller --clean --workpath build\output build\LoLDataCollector.spec
) else (
    echo Spec file not found, using direct PyInstaller command...
    python -m PyInstaller --clean --onefile --noconsole --name LoLDataCollector --icon=%cd%\resources\icon.ico --manifest=%cd%\uac_admin.manifest --specpath=build --workpath=build\output %cd%\main.py
)

echo.
if %errorlevel% equ 0 (
    echo Build completed successfully!
    echo The executable is located in the 'dist' directory.
) else (
    echo Build failed with error code: %errorlevel%
)

pause
