@echo off
echo ========================================
echo Python 3.13 Compatibility Fix
echo ========================================
echo.

echo Upgrading pip, setuptools, and wheel...
python -m pip install --upgrade pip setuptools wheel

echo.
echo Installing packages with Python 3.13 compatibility...
echo.

echo [1/8] Installing CustomTkinter...
python -m pip install --no-cache-dir customtkinter>=5.3.0

echo [2/8] Installing NumPy...
python -m pip install --no-cache-dir numpy>=1.26.0

echo [3/8] Installing Pillow...
python -m pip install --no-cache-dir Pillow>=10.1.0

echo [4/8] Installing OpenCV...
python -m pip install --no-cache-dir opencv-python>=4.9.0

echo [5/8] Installing Matplotlib...
python -m pip install --no-cache-dir matplotlib>=3.8.0

echo [6/8] Installing Pandas...
python -m pip install --no-cache-dir pandas>=2.1.0

echo [7/8] Installing pyttsx3...
python -m pip install --no-cache-dir pyttsx3>=2.90

echo [8/8] Installing ReportLab...
python -m pip install --no-cache-dir reportlab>=4.0.0

echo.
echo ========================================
echo Installation completed!
echo ========================================
echo.

REM Test imports
echo Testing package imports...
python -c "
try:
    import customtkinter
    print('✅ CustomTkinter: OK')
except Exception as e:
    print('❌ CustomTkinter: FAILED -', str(e))

try:
    import cv2
    print('✅ OpenCV: OK')
except Exception as e:
    print('❌ OpenCV: FAILED -', str(e))

try:
    import matplotlib
    print('✅ Matplotlib: OK')
except Exception as e:
    print('❌ Matplotlib: FAILED -', str(e))

try:
    import numpy
    print('✅ NumPy: OK')
except Exception as e:
    print('❌ NumPy: FAILED -', str(e))

try:
    import PIL
    print('✅ Pillow: OK')
except Exception as e:
    print('❌ Pillow: FAILED -', str(e))

try:
    import pyttsx3
    print('✅ pyttsx3: OK')
except Exception as e:
    print('❌ pyttsx3: FAILED -', str(e))

try:
    import reportlab
    print('✅ ReportLab: OK')
except Exception as e:
    print('❌ ReportLab: FAILED -', str(e))

try:
    import pandas
    print('✅ Pandas: OK')
except Exception as e:
    print('❌ Pandas: FAILED -', str(e))
"

echo.
echo If all packages show ✅, you can now run ErgoVision!
echo.
pause
