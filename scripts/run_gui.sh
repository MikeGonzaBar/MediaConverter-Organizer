#!/bin/bash

echo "Media Converter & Organizer GUI"
echo "================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.10+ from your package manager or https://python.org"
    exit 1
fi

# Check Python version
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
required_version="3.10"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "ERROR: Python 3.10+ is required. Found Python $python_version"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment"
        exit 1
    fi
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate virtual environment"
    exit 1
fi

# Clean up corrupted pip distributions before installing
echo "Cleaning up corrupted pip distributions..."
find .venv/lib/python*/site-packages -maxdepth 1 -type d -name "~ip*" -exec rm -rf {} + 2>/dev/null || true

# Install/update requirements
echo "Installing requirements..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install requirements"
    exit 1
fi

# Check if main scripts exist
if [ ! -f "src/image_organizer.py" ]; then
    echo "ERROR: src/image_organizer.py not found"
    echo "Please ensure you're running this from the correct directory"
    exit 1
fi

if [ ! -f "src/wav_to_flac_converter.py" ]; then
    echo "ERROR: src/wav_to_flac_converter.py not found"
    echo "Please ensure you're running this from the correct directory"
    exit 1
fi

# Run the GUI
echo "Starting Media Converter & Organizer GUI..."
echo
python3 main.py

# Check exit status
if [ $? -ne 0 ]; then
    echo
    echo "An error occurred. Press Enter to exit."
    read
fi
