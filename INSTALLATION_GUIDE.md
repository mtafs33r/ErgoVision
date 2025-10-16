# ErgoVision Installation & Setup Guide

## Option 1: Install Python and Run Directly (Recommended)

### Step 1: Install Python
1. Go to [python.org](https://www.python.org/downloads/)
2. Download Python 3.10 or newer for Windows
   - **For Python 3.13**: Use the special compatibility scripts below
   - **For Python 3.10-3.12**: Use the standard installation
3. **IMPORTANT**: During installation, check "Add Python to PATH"
4. Complete the installation

### Step 1.5: Python 3.13 Special Instructions
If you have Python 3.13 installed, use these special scripts:

1. **Fix Python 3.13 compatibility issues:**
   ```cmd
   fix_python313.bat
   ```

2. **Run ErgoVision with Python 3.13:**
   ```cmd
   run_with_python313.bat
   ```

### Step 2: Verify Python Installation
Open Command Prompt (cmd) and run:
```cmd
python --version
```
You should see something like: `Python 3.10.x`

### Step 3: Install Dependencies
Navigate to the ErgoVision folder and run:
```cmd
pip install -r requirements.txt
```

### Step 4: Run the Application
```cmd
python main.py
```

---

## Option 2: Create Executable File (Standalone)

### Prerequisites
- Python must be installed (from Option 1)

### Step 1: Install PyInstaller
```cmd
pip install pyinstaller
```

### Step 2: Build Executable
```cmd
python build.py
```

### Step 3: Find Your Executable
The executable will be created in the `dist` folder:
```
dist/ErgoVision.exe
```

You can now double-click `ErgoVision.exe` to run the application without needing Python installed on other computers.

---

## Option 3: Quick Setup Script

I've created a setup script for you. Run this in Command Prompt:

```cmd
setup_ergovision.bat
```

---

## Option 4: Manual Installation

If you prefer to install dependencies manually:

```cmd
pip install customtkinter==5.2.2
pip install opencv-python==4.8.1.78
pip install matplotlib==3.8.2
pip install numpy==1.24.3
pip install Pillow==10.1.0
pip install pyttsx3==2.90
pip install reportlab==4.0.7
pip install pandas
```

---

## Troubleshooting

### "Python not found" Error
- Install Python from [python.org](https://www.python.org/downloads/)
- Make sure to check "Add Python to PATH" during installation
- Restart Command Prompt after installation

### "pip not found" Error
- Try: `python -m pip install package_name`
- Or reinstall Python with PATH option checked

### Python 3.13 Compatibility Issues
If you're using Python 3.13 and getting installation errors:

1. **Run the Python 3.13 fix script:**
   ```cmd
   fix_python313.bat
   ```

2. **If that doesn't work, try manual installation:**
   ```cmd
   python -m pip install --upgrade pip setuptools wheel
   python -m pip install --no-cache-dir customtkinter>=5.3.0
   python -m pip install --no-cache-dir numpy>=1.26.0
   python -m pip install --no-cache-dir opencv-python>=4.9.0
   python -m pip install --no-cache-dir matplotlib>=3.8.0
   python -m pip install --no-cache-dir pandas>=2.1.0
   python -m pip install --no-cache-dir pyttsx3>=2.90
   python -m pip install --no-cache-dir reportlab>=4.0.0
   ```

3. **Alternative: Downgrade to Python 3.12:**
   - Python 3.12 has better package compatibility
   - Download from [python.org](https://www.python.org/downloads/)

### Camera Issues
- Make sure no other applications are using your camera
- Check Windows camera permissions
- Try running as administrator

### Voice Assistant Issues
- Install additional TTS engines if needed
- Check Windows audio settings
- Voice can be disabled in app settings

---

## Quick Start Guide

1. **First Time Setup:**
   - Create an account or login
   - Complete your profile information
   - Allow camera access when prompted

2. **Using the App:**
   - Click "Start Monitoring" in the Monitoring tab
   - Follow the posture feedback
   - Check the AI Coach for personalized tips
   - View your progress in Reports

3. **Features to Explore:**
   - Daily inspirational quotes on the dashboard
   - Voice assistant feedback (if enabled)
   - Smart reminders for posture breaks
   - Export your data to CSV or PDF

---

## System Requirements

- Windows 10/11
- Python 3.10+ (if running from source)
- Webcam/Camera
- 4GB RAM minimum
- 100MB free disk space
- Audio device (for voice features)

---

## Support

If you encounter any issues:
1. Check the troubleshooting section above
2. Make sure all dependencies are installed
3. Verify your camera and audio devices work
4. Try running as administrator

The application will create a local database file (`ergovision.db`) to store your data.
