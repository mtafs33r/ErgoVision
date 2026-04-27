@echo off
title ErgoVision Quick Start
color 0A

echo.
echo    ███████╗██████╗  ██████╗  ██████╗ ██╗   ██╗██╗███████╗██╗ ██████╗ ███╗   ██╗
echo    ██╔════╝██╔══██╗██╔════╝ ██╔═══██╗██║   ██║██║██╔════╝██║██╔═══██╗████╗  ██║
echo    █████╗  ██████╔╝██║  ███╗██║   ██║██║   ██║██║███████╗██║██║   ██║██╔██╗ ██║
echo    ██╔══╝  ██╔══██╗██║   ██║██║   ██║╚██╗ ██╔╝██║╚════██║██║██║   ██║██║╚██╗██║
echo    ███████╗██║  ██║╚██████╔╝╚██████╔╝ ╚████╔╝ ██║███████║██║╚██████╔╝██║ ╚████║
echo    ╚══════╝╚═╝  ╚═╝ ╚═════╝  ╚═════╝   ╚═══╝  ╚═╝╚══════╝╚═╝ ╚═════╝ ╚═╝  ╚═══╝
echo.
echo                           AI Posture ^& Health Coach
echo.
echo ================================================================================
echo.

REM Check if Python is installed
echo [1/3] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found!
    echo.
    echo Please install Python first:
    echo 1. Go to https://www.python.org/downloads/
    echo 2. Download Python 3.10 or newer
    echo 3. IMPORTANT: Check "Add Python to PATH" during installation
    echo 4. Restart this script after installation
    echo.
    pause
    exit /b 1
) else (
    echo ✅ Python found!
)

echo.
echo [2/3] Checking dependencies...
python -c "import customtkinter; import mediapipe" >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Dependencies not installed!
    echo.
    echo Running setup script...
    call setup_ergovision.bat
    if %errorlevel% neq 0 (
        echo Setup failed! Please check the installation guide.
        pause
        exit /b 1
    )
) else (
    echo ✅ Dependencies ready!
)

echo.
echo [3/3] Starting ErgoVision...
echo.

REM Try to run executable first
if exist "dist\ErgoVision.exe" (
    echo 🚀 Launching ErgoVision executable...
    start "" "dist\ErgoVision.exe"
) else (
    echo 🚀 Launching ErgoVision from source...
    python main.py
    if %errorlevel% neq 0 (
        echo.
        echo ❌ ErgoVision exited with an error!
        pause
    )
)

echo.
echo ================================================================================
echo ErgoVision is starting! Please wait...
echo.
echo If the application doesn't start:
echo - Check your camera permissions
echo - Make sure no other apps are using your camera
echo - Try running as administrator
echo.
echo For help, see INSTALLATION_GUIDE.md
echo ================================================================================
