@echo off
echo Media Converter ^& Organizer GUI
echo ================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7+ from https://python.org
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Install/update requirements
echo Installing requirements...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install requirements
    pause
    exit /b 1
)

REM Check if main scripts exist
if not exist "image_organizer.py" (
    echo ERROR: image_organizer.py not found
    echo Please ensure you're running this from the correct directory
    pause
    exit /b 1
)

if not exist "wav_to_flac_converter.py" (
    echo ERROR: wav_to_flac_converter.py not found
    echo Please ensure you're running this from the correct directory
    pause
    exit /b 1
)

REM Run the GUI
echo Starting Media Converter ^& Organizer GUI...
echo.
python media_converter_organizer_gui.py

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo An error occurred. Press any key to exit.
    pause
)
