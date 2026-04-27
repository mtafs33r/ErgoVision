@echo off
echo ========================================
echo ErgoVision Setup Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo Python found! Installing dependencies...
echo.

REM Check Python version and use appropriate requirements
echo Checking Python version...
python -c "import sys; print('Python version:', sys.version)" 2>nul
python -c "import sys; exit(0 if sys.version_info >= (3, 13) else 1)" 2>nul
if %errorlevel% equ 0 (
    echo Using Python 3.13+ compatible requirements...
    if exist "requirements_python313.txt" (
        python -m pip install -r requirements_python313.txt
    ) else (
        echo Installing packages individually for Python 3.13+...
        python -m pip install --upgrade pip setuptools wheel
        python -m pip install customtkinter>=5.3.0
        python -m pip install opencv-python>=4.9.0
        python -m pip install matplotlib>=3.8.0
        python -m pip install numpy>=1.26.0
        python -m pip install Pillow>=10.1.0
        python -m pip install pyttsx3>=2.90
        python -m pip install reportlab>=4.0.0
        python -m pip install pandas>=2.1.0
        python -m pip install mediapipe>=0.10.0
        python -m pip install pymongo
        python -m pip install python-dotenv
        python -m pip install google-generativeai
    )
) else (
    echo Using standard requirements...
    if exist "requirements.txt" (
        python -m pip install -r requirements.txt
    ) else (
        echo Installing packages individually...
        python -m pip install --upgrade pip setuptools wheel
        python -m pip install customtkinter>=5.2.0
        python -m pip install opencv-python>=4.8.0
        python -m pip install matplotlib>=3.7.0
        python -m pip install numpy>=1.24.0
        python -m pip install Pillow>=10.0.0
        python -m pip install pyttsx3>=2.90
        python -m pip install reportlab>=4.0.0
        python -m pip install pandas>=2.0.0
    )
)

echo.
echo ========================================
echo Dependencies installed successfully!
echo ========================================
echo.

REM Ask user if they want to create executable
set /p create_exe="Do you want to create a standalone executable? (y/n): "
if /i "%create_exe%"=="y" (
    echo.
    echo Installing PyInstaller...
    python -m pip install pyinstaller
    
    echo.
    echo Creating executable...
    python build.py
    
    if exist "dist\ErgoVision.exe" (
        echo.
        echo ========================================
        echo SUCCESS! Executable created!
        echo Location: dist\ErgoVision.exe
        echo ========================================
        echo.
        set /p run_now="Do you want to run ErgoVision now? (y/n): "
        if /i "%run_now%"=="y" (
            start "" "dist\ErgoVision.exe"
        )
    ) else (
        echo.
        echo Failed to create executable. You can still run the app with: python main.py
    )
) else (
    echo.
    echo Setup complete! You can now run ErgoVision with: python main.py
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To run ErgoVision:
echo   - From source: python main.py
echo   - Executable: dist\ErgoVision.exe (if created)
echo.
echo For help, see INSTALLATION_GUIDE.md
echo.
pause
