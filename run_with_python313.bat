@echo off
echo ========================================
echo ErgoVision - Python 3.13 Compatible
echo ========================================
echo.

REM Check if Python 3.13 is detected
python -c "import sys; print('Python version:', sys.version)" 2>nul
python -c "import sys; exit(0 if sys.version_info >= (3, 13) else 1)" 2>nul
if %errorlevel% neq 0 (
    echo This script is optimized for Python 3.13+
    echo You can still run it, but you might encounter compatibility issues.
    echo.
)

REM Check if packages are installed
echo Checking dependencies...
python -c "import customtkinter" 2>nul
if %errorlevel% neq 0 (
    echo Dependencies not found! Running Python 3.13 fix...
    call fix_python313.bat
    if %errorlevel% neq 0 (
        echo Failed to install dependencies. Please run fix_python313.bat manually.
        pause
        exit /b 1
    )
)

REM Try to run executable first
if exist "dist\ErgoVision.exe" (
    echo Found executable! Starting ErgoVision...
    start "" "dist\ErgoVision.exe"
    exit /b 0
)

REM Run from source
if exist "main.py" (
    echo Starting ErgoVision from source...
    python main.py
) else (
    echo ERROR: main.py not found!
    echo Please make sure you're in the ErgoVision directory.
    pause
    exit /b 1
)
