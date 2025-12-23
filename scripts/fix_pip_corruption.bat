@echo off
REM Fix corrupted pip distributions in virtual environment
echo Fixing corrupted pip distributions...
echo.

REM Check if venv exists
if not exist ".venv" (
    echo ERROR: Virtual environment not found
    echo Please run setup.bat first
    pause
    exit /b 1
)

REM Remove corrupted pip distributions
echo Removing corrupted pip distributions...
for /d %%d in (.venv\Lib\site-packages\~ip*) do (
    if exist "%%d" (
        echo Removing: %%d
        rmdir /s /q "%%d" 2>nul
    )
)

REM Reinstall pip
echo.
echo Reinstalling pip...
call .venv\Scripts\activate.bat
python -m ensurepip --upgrade
python -m pip install --upgrade pip

echo.
echo Done! Corrupted distributions removed and pip reinstalled.
pause

