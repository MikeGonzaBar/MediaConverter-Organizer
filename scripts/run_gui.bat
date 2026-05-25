@echo off
echo Media Converter ^& Organizer GUI
echo ================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

python -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)"
if errorlevel 1 (
    echo ERROR: Python 3.10+ is required
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

REM Clean up corrupted pip distributions before installing
echo Cleaning up corrupted pip distributions...
for /d %%d in (.venv\Lib\site-packages\~ip*) do (
    if exist "%%d" (
        echo Removing corrupted distribution: %%d
        rmdir /s /q "%%d" 2>nul
    )
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

REM Run the GUI
echo Starting Media Converter ^& Organizer GUI...
echo.
python main.py

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo An error occurred. Press any key to exit.
    pause
)
