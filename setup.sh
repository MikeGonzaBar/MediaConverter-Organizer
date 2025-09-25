#!/bin/bash

echo "Media Converter & Organizer - Setup Script"
echo "=========================================="
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.7+ from your package manager or https://python.org"
    exit 1
fi

echo "Python found. Checking version..."
python3 --version

# Check Python version
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
required_version="3.7"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "ERROR: Python 3.7+ is required. Found Python $python_version"
    exit 1
fi

# Remove existing virtual environment if it exists
if [ -d ".venv" ]; then
    echo
    echo "Removing existing virtual environment..."
    rm -rf .venv
fi

# Create new virtual environment
echo
echo "Creating unified virtual environment..."
python3 -m venv .venv
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create virtual environment"
    exit 1
fi

# Activate virtual environment
echo
echo "Activating virtual environment..."
source .venv/bin/activate
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to activate virtual environment"
    exit 1
fi

# Upgrade pip
echo
echo "Upgrading pip..."
python -m pip install --upgrade pip

# Install requirements
echo
echo "Installing all dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install requirements"
    exit 1
fi

# Check if main scripts exist
echo
echo "Checking project structure..."
if [ ! -f "image_organizer.py" ]; then
    echo "ERROR: image_organizer.py not found"
    echo "Please ensure you're running this from the correct directory"
    exit 1
fi

if [ ! -f "wav_to_flac_converter.py" ]; then
    echo "ERROR: wav_to_flac_converter.py not found"
    echo "Please ensure you're running this from the correct directory"
    exit 1
fi

echo
echo "=========================================="
echo "Setup completed successfully!"
echo "=========================================="
echo
echo "You can now run:"
echo "  - GUI: ./run_gui.sh"
echo "  - Or manually: python3 media_converter_organizer_gui.py"
echo
echo "To activate the virtual environment manually:"
echo "  source .venv/bin/activate"
echo
