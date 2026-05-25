@echo off
echo Media Converter ^& Organizer - Setup Script
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

echo Python found. Checking version...
python --version
python -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)"
if errorlevel 1 (
    echo ERROR: Python 3.10+ is required
    pause
    exit /b 1
)

REM Remove existing virtual environment if it exists
if exist ".venv" (
    echo.
    echo Removing existing virtual environment...
    rmdir /s /q .venv 2>nul
    if exist ".venv" (
        echo WARNING: Could not remove existing .venv directory
        echo This may be due to permission issues or files in use
        echo.
        echo Please try one of the following:
        echo 1. Run this script as Administrator
        echo 2. Manually delete the .venv folder
        echo 3. Run scripts\fix_pip_corruption.bat if pip metadata is corrupted
        echo.
        echo Attempting to continue with existing .venv...
    ) else (
        echo Successfully removed existing virtual environment
    )
)

REM Create new virtual environment
echo.
if exist ".venv" (
    echo Using existing virtual environment...
) else (
    echo Creating unified virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo.
echo Activating virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Upgrade pip
echo.
echo Upgrading pip...
python -m pip install --upgrade pip

REM Clean up corrupted pip distributions before installing
echo.
echo Cleaning up corrupted pip distributions...
for /d %%d in (.venv\Lib\site-packages\~ip*) do (
    if exist "%%d" (
        echo Removing corrupted distribution: %%d
        rmdir /s /q "%%d" 2>nul
    )
)

REM Install requirements
echo.
echo Installing all dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install requirements
    pause
    exit /b 1
)

REM Check if main scripts exist
echo.
echo Checking project structure...
if not exist "src\image_organizer.py" (
    echo ERROR: src\image_organizer.py not found
    echo Please ensure you're running this from the correct directory
    pause
    exit /b 1
)

if not exist "src\wav_to_flac_converter.py" (
    echo ERROR: src\wav_to_flac_converter.py not found
    echo Please ensure you're running this from the correct directory
    pause
    exit /b 1
)

echo.
echo ==========================================
echo Setup completed successfully!
echo ==========================================
echo.
echo You can now run:
echo   - GUI: scripts\run_gui.bat
echo   - Or manually: python main.py
echo.
echo To activate the virtual environment manually:
echo   .venv\Scripts\activate.bat
echo.
pause
