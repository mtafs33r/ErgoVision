"""
Build script for ErgoVision application
Creates a standalone executable using PyInstaller
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_pyinstaller():
    """Check if PyInstaller is installed"""
    try:
        import PyInstaller
        return True
    except ImportError:
        return False

def install_pyinstaller():
    """Install PyInstaller"""
    print("Installing PyInstaller...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

def clean_build_dirs():
    """Clean previous build directories"""
    dirs_to_clean = ["build", "dist", "__pycache__"]
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"Cleaning {dir_name}...")
            shutil.rmtree(dir_name)
    
    # Clean .spec files
    spec_files = [f for f in os.listdir(".") if f.endswith(".spec")]
    for spec_file in spec_files:
        os.remove(spec_file)
        print(f"Removed {spec_file}")

def create_icon():
    """Create a simple icon file if it doesn't exist"""
    icon_path = "icon.ico"
    if not os.path.exists(icon_path):
        print("Creating placeholder icon...")
        # Create a simple 32x32 icon (this is a placeholder)
        # In a real application, you would use a proper icon file
        try:
            from PIL import Image, ImageDraw
            
            # Create a simple icon
            img = Image.new('RGBA', (32, 32), (58, 127, 246, 255))  # Blue background
            draw = ImageDraw.Draw(img)
            
            # Draw a simple "E" for ErgoVision
            draw.text((8, 8), "E", fill=(255, 255, 255, 255))
            
            # Save as ICO
            img.save(icon_path, format='ICO')
            print(f"Created placeholder icon: {icon_path}")
        except ImportError:
            print("PIL not available for icon creation. Skipping icon.")

def build_executable():
    """Build the executable using PyInstaller"""
    print("Building executable...")
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--onefile",                    # Single executable file
        "--windowed",                   # No console window
        "--name=ErgoVision",           # Executable name
        "--clean",                     # Clean build
        "--noconfirm",                 # Don't ask for confirmation
    ]
    
    # Add icon if it exists
    if os.path.exists("icon.ico"):
        cmd.extend(["--icon=icon.ico"])
    
    # Add hidden imports for better compatibility
    hidden_imports = [
        "customtkinter",
        "cv2",
        "matplotlib.backends.backend_tkagg",
        "PIL",
        "numpy",
        "pandas",
        "pyttsx3",
        "reportlab",
        "sqlite3",
        "threading",
        "queue"
    ]
    
    for imp in hidden_imports:
        cmd.extend(["--hidden-import", imp])
    
    # Add data files
    data_files = [
        ("config.json", "."),
        ("requirements.txt", ".")
    ]
    
    for src, dst in data_files:
        if os.path.exists(src):
            cmd.extend(["--add-data", f"{src};{dst}"])
    
    # Main script
    cmd.append("main.py")
    
    print(f"Running command: {' '.join(cmd)}")
    
    try:
        subprocess.check_call(cmd)
        print("Build completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Build failed with error: {e}")
        return False

def create_installer_info():
    """Create installer information file"""
    info_content = """ErgoVision - AI Posture & Health Coach
Version: 1.0.0

Installation Instructions:
1. Run ErgoVision.exe
2. The application will create necessary database files automatically
3. Create an account or login to start using the application

System Requirements:
- Windows 10/11
- Webcam/Camera
- 100MB free disk space
- 4GB RAM minimum

Features:
- Real-time posture monitoring
- AI-powered health coaching
- Comprehensive analytics
- Voice assistant
- Smart reminders
- Daily motivational quotes

For support or issues, please refer to the README.md file.
"""
    
    with open("INSTALLER_INFO.txt", "w") as f:
        f.write(info_content)
    
    print("Created INSTALLER_INFO.txt")

def main():
    """Main build function"""
    print("ErgoVision Build Script")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("main.py"):
        print("Error: main.py not found. Please run this script from the ErgoVision directory.")
        return False
    
    # Check/install PyInstaller
    if not check_pyinstaller():
        print("PyInstaller not found. Installing...")
        install_pyinstaller()
    
    # Clean previous builds
    clean_build_dirs()
    
    # Create icon
    create_icon()
    
    # Build executable
    if build_executable():
        print("\n" + "=" * 50)
        print("Build completed successfully!")
        print(f"Executable location: {os.path.join('dist', 'ErgoVision.exe')}")
        
        # Create installer info
        create_installer_info()
        
        # Copy additional files to dist
        additional_files = ["README.md", "INSTALLER_INFO.txt"]
        for file_name in additional_files:
            if os.path.exists(file_name):
                shutil.copy2(file_name, "dist/")
                print(f"Copied {file_name} to dist/")
        
        print("\nDistribution package ready in 'dist/' folder!")
        print("You can now distribute the ErgoVision.exe file along with the documentation.")
        
        return True
    else:
        print("Build failed!")
        return False

if __name__ == "__main__":
    success = main()
    input("\nPress Enter to exit...")
    sys.exit(0 if success else 1)
