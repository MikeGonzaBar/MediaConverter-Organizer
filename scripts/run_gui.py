#!/usr/bin/env python3
"""
Cross-Platform Media Converter & Organizer GUI Launcher
Works on Windows, Linux, and macOS
"""

import sys
import os
import subprocess
import platform
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.10+"""
    if sys.version_info < (3, 10):
        print("ERROR: Python 3.10+ is required")
        print(f"Current version: {sys.version}")
        return False
    return True

def check_dependencies():
    """Check for required external dependencies"""
    missing_deps = []
    
    # Check for ffmpeg
    if not shutil_which("ffmpeg"):
        missing_deps.append("ffmpeg")
    
    # Check for fpcalc (optional, for audio fingerprinting)
    fpcalc_missing = not shutil_which("fpcalc")
    
    if missing_deps:
        print("\nWARNING: Missing required dependencies:")
        for dep in missing_deps:
            print(f"   - {dep}")
        print("\nInstallation instructions:")
        print_installation_instructions(missing_deps, fpcalc_missing)
        return False
    
    if fpcalc_missing:
        print("\nWARNING: Optional dependency missing:")
        print("   - fpcalc (Chromaprint) - Required for audio fingerprinting")
        print("   Audio fingerprinting features will be disabled.")
        print_installation_instructions([], True)
    
    return True

def shutil_which(cmd):
    """Cross-platform check for command availability"""
    import shutil
    return shutil.which(cmd) is not None

def print_installation_instructions(missing_deps, fpcalc_missing):
    """Print platform-specific installation instructions"""
    system = platform.system()
    
    print(f"\nInstallation for {system}:")
    print("=" * 50)
    
    if "ffmpeg" in missing_deps:
        if system == "Windows":
            print("FFmpeg:")
            print("  1. winget install ffmpeg")
            print("  2. Or download from: https://ffmpeg.org/download.html")
            print("  3. Add to PATH")
        elif system == "Darwin":  # macOS
            print("FFmpeg:")
            print("  brew install ffmpeg")
        else:  # Linux
            print("FFmpeg:")
            print("  Ubuntu/Debian: sudo apt install ffmpeg")
            print("  Fedora: sudo dnf install ffmpeg")
            print("  Arch: sudo pacman -S ffmpeg")
    
    if fpcalc_missing:
        if system == "Windows":
            print("\nChromaprint (fpcalc):")
            print("  1. Download from: https://acoustid.org/chromaprint")
            print("  2. Extract and add to PATH")
        elif system == "Darwin":  # macOS
            print("\nChromaprint (fpcalc):")
            print("  brew install chromaprint")
        else:  # Linux
            print("\nChromaprint (fpcalc):")
            print("  Ubuntu/Debian: sudo apt install chromaprint-tools")
            print("  Fedora: sudo dnf install chromaprint-tools")
            print("  Arch: sudo pacman -S chromaprint")
    
    print("=" * 50)

def setup_virtual_environment():
    """Set up virtual environment if it doesn't exist"""
    venv_path = Path(".venv")
    
    if not venv_path.exists():
        print("Creating virtual environment...")
        try:
            subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True)
            print("OK: Virtual environment created")
        except subprocess.CalledProcessError:
            print("ERROR: Failed to create virtual environment")
            return False
    
    return True

def get_python_executable():
    """Get the Python executable path (handles venv activation)"""
    system = platform.system()
    venv_path = Path(".venv")
    
    if venv_path.exists():
        if system == "Windows":
            python_exe = venv_path / "Scripts" / "python.exe"
        else:
            python_exe = venv_path / "bin" / "python"
        
        if python_exe.exists():
            return str(python_exe)
    
    # Fallback to system Python
    return sys.executable

def check_pip_working(python_exe):
    """Check if pip is working correctly"""
    try:
        result = subprocess.run(
            [python_exe, "-m", "pip", "--version"],
            check=False,
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except Exception:
        return False

def fix_pip(python_exe):
    """Fix broken pip installation"""
    print("WARNING: pip appears to be broken. Attempting to fix...")
    
    # Method 1: Try ensurepip (built-in)
    try:
        print("Trying ensurepip (built-in)...")
        result = subprocess.run(
            [python_exe, "-m", "ensurepip", "--upgrade"],
            check=False,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            print("OK: pip fixed using ensurepip")
            return True
    except Exception as e:
        print(f"ensurepip failed: {e}")
    
    # Method 2: Download and run get-pip.py
    try:
        import urllib.request
        import tempfile
        
        print("Downloading get-pip.py...")
        get_pip_url = "https://bootstrap.pypa.io/get-pip.py"
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.py')
        temp_file.close()
        
        try:
            urllib.request.urlretrieve(get_pip_url, temp_file.name)
            print("Installing pip using get-pip.py...")
            result = subprocess.run(
                [python_exe, temp_file.name],
                check=False,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Clean up
            try:
                import os
                os.unlink(temp_file.name)
            except Exception:
                pass
            
            if result.returncode == 0:
                print("OK: pip fixed using get-pip.py")
                return True
            else:
                print(f"get-pip.py failed: {result.stderr[:200] if result.stderr else 'Unknown error'}")
        except Exception as e:
            print(f"Failed to download/run get-pip.py: {e}")
            # Clean up on error
            try:
                import os
                if os.path.exists(temp_file.name):
                    os.unlink(temp_file.name)
            except Exception:
                pass
    except Exception as e:
        print(f"Error fixing pip: {e}")
    
    return False

def install_requirements():
    """Install requirements if needed"""
    python_exe = get_python_executable()
    requirements_file = Path("requirements.txt")
    
    if not requirements_file.exists():
        print("WARNING: requirements.txt not found")
        return True
    
    print("Checking and installing dependencies...")
    
    # First, check if pip is working
    if not check_pip_working(python_exe):
        print("WARNING: pip is not working correctly")
        if not fix_pip(python_exe):
            print("\nERROR: Could not fix pip installation")
            print("Please try one of the following:")
            print("  1. Delete .venv folder and run setup again")
            print("  2. Recreate virtual environment: python -m venv .venv --clear")
            print("  3. Install pip manually: python -m ensurepip --upgrade")
            return False
        
        # Verify pip is now working
        if not check_pip_working(python_exe):
            print("ERROR: pip is still not working after fix attempt")
            return False
    
    # Always try to install/upgrade requirements to ensure everything is available
    try:
        # Upgrade pip first
        print("Upgrading pip...")
        result = subprocess.run(
            [python_exe, "-m", "pip", "install", "--upgrade", "pip"],
            check=False,
            capture_output=True,
            text=True,
            timeout=60
        )
        if result.returncode == 0:
            print("OK: pip upgraded")
        else:
            print("WARNING: pip upgrade had issues (continuing anyway)")
        
        # Install requirements
        print("Installing requirements from requirements.txt...")
        result = subprocess.run(
            [python_exe, "-m", "pip", "install", "-r", "requirements.txt"],
            check=False,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )
        
        if result.returncode == 0:
            print("OK: Requirements installed/updated successfully")
            return True
        else:
            print("WARNING: Some requirements may have failed to install")
            if result.stderr:
                error_msg = result.stderr[:500]
                print(f"Error output: {error_msg}")
            print("\nYou may need to install them manually:")
            print(f"  {python_exe} -m pip install -r requirements.txt")
            # Don't fail completely - let the app try to run anyway
            return True
            
    except subprocess.TimeoutExpired:
        print("WARNING: Installation timed out")
        print("This may happen with slow internet connections")
        print("You can try installing manually:")
        print(f"  {python_exe} -m pip install -r requirements.txt")
        return True
    except Exception as e:
        print(f"WARNING: Error installing requirements: {e}")
        print("You may need to install them manually:")
        print(f"  {python_exe} -m pip install -r requirements.txt")
        return True  # Continue anyway

def check_tkinter():
    """Check if tkinter is available (required for GUI)"""
    try:
        import tkinter
        return True
    except ImportError:
        system = platform.system()
        print("\nERROR: tkinter is not available")
        print("This is required for the GUI.")
        
        if system == "Linux":
            print("\nInstall tkinter:")
            print("  Ubuntu/Debian: sudo apt install python3-tk")
            print("  Fedora: sudo dnf install python3-tkinter")
            print("  Arch: sudo pacman -S tk")
        elif system == "Darwin":
            print("\nInstall tkinter:")
            print("  macOS usually includes tkinter with Python")
            print("  If missing, reinstall Python from python.org")
        else:
            print("\nInstall tkinter:")
            print("  Windows usually includes tkinter with Python")
            print("  If missing, reinstall Python from python.org")
        
        return False

def main():
    """Main launcher function"""
    print("Media Converter & Organizer - Cross-Platform Launcher")
    print("=" * 60)
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version.split()[0]}")
    print("=" * 60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check tkinter (required for GUI)
    if not check_tkinter():
        sys.exit(1)
    
    # Setup virtual environment
    if not setup_virtual_environment():
        sys.exit(1)
    
    # Install requirements (with pip fix if needed)
    if not install_requirements():
        print("\nWARNING: Requirements installation had issues")
        print("You may need to recreate the virtual environment:")
        print("  1. Delete .venv folder")
        print("  2. Run this script again")
        print("  Or manually: python -m venv .venv --clear")
        
        # Ask user if they want to recreate venv
        try:
            response = input("\nWould you like to recreate the virtual environment? (y/n): ").strip().lower()
            if response == 'y':
                print("\nRecreating virtual environment...")
                import shutil
                venv_path = Path(".venv")
                if venv_path.exists():
                    shutil.rmtree(venv_path)
                if setup_virtual_environment():
                    if install_requirements():
                        print("OK: Virtual environment recreated and requirements installed")
                    else:
                        print("WARNING: Still having issues. Please check the errors above.")
                        sys.exit(1)
                else:
                    print("ERROR: Failed to recreate virtual environment")
                    sys.exit(1)
            else:
                print("Continuing with existing setup...")
        except (KeyboardInterrupt, EOFError):
            print("\n\nExiting...")
            sys.exit(1)
    
    # Verify critical dependencies are installed
    print("\nVerifying critical dependencies...")
    missing_critical = []
    
    # Check tkinter
    try:
        import tkinter  # noqa: F401
        print("OK: tkinter: Available")
    except ImportError:
        missing_critical.append("tkinter")
        print("ERROR: tkinter: Missing")
    
    # Check Pillow
    try:
        from PIL import Image  # noqa: F401
        print("OK: Pillow (PIL): Available")
    except ImportError:
        missing_critical.append("Pillow")
        print("ERROR: Pillow (PIL): Missing")
    
    if missing_critical:
        print(f"\nWARNING: Missing critical dependencies: {', '.join(missing_critical)}")
        print("Attempting to install...")
        python_exe = get_python_executable()
        
        # Map dependency names to pip package names
        dep_map = {
            "tkinter": None,  # tkinter is usually system-installed
            "Pillow": "Pillow"
        }
        
        for dep in missing_critical:
            pip_name = dep_map.get(dep, dep)
            if pip_name is None:
                print(f"WARNING: {dep} cannot be installed via pip (usually system-installed)")
                continue
                
            try:
                print(f"Installing {pip_name}...")
                result = subprocess.run(
                    [python_exe, "-m", "pip", "install", pip_name],
                    check=False,
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    print(f"OK: Installed {pip_name}")
                else:
                    print(f"ERROR: Failed to install {pip_name}")
                    print(f"  Error: {result.stderr[:200] if result.stderr else 'Unknown error'}")
            except Exception as e:
                print(f"ERROR: Error installing {pip_name}: {e}")
        
        # Check again after installation attempts
        still_missing = []
        if "tkinter" in missing_critical:
            try:
                import tkinter  # noqa: F401
            except ImportError:
                still_missing.append("tkinter")
        
        if "Pillow" in missing_critical:
            try:
                from PIL import Image  # noqa: F401
            except ImportError:
                still_missing.append("Pillow")
        
        if still_missing:
            print(f"\nERROR: Critical dependencies still missing: {', '.join(still_missing)}")
            print("\nPlease install them manually:")
            python_exe = get_python_executable()
            for dep in still_missing:
                pip_name = dep_map.get(dep, dep)
                if pip_name:
                    print(f"  {python_exe} -m pip install {pip_name}")
                else:
                    print(f"  {dep} needs to be installed via system package manager")
            sys.exit(1)
    
    # Check external dependencies (non-blocking warning)
    check_dependencies()
    
    # Check if main script exists
    main_script = Path("main.py")
    if not main_script.exists():
        print(f"\nERROR: {main_script} not found")
        print("Please ensure you're running this from the project directory")
        sys.exit(1)
    
    # Launch GUI
    print("\nStarting Media Converter & Organizer GUI...")
    print("=" * 60)
    
    python_exe = get_python_executable()
    
    try:
        subprocess.run([python_exe, str(main_script)], check=True)
    except KeyboardInterrupt:
        print("\n\nLauncher interrupted by user")
        sys.exit(0)
    except subprocess.CalledProcessError as e:
        print(f"\nERROR: Error running GUI: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"\nERROR: Python executable not found: {python_exe}")
        print("Please ensure Python is properly installed")
        sys.exit(1)

if __name__ == "__main__":
    main()

