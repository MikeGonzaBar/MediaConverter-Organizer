#!/bin/bash
# Fix corrupted pip distributions in virtual environment

echo "Fixing corrupted pip distributions..."
echo

# Check if venv exists
if [ ! -d ".venv" ]; then
    echo "ERROR: Virtual environment not found"
    echo "Please run setup.sh first"
    exit 1
fi

# Remove corrupted pip distributions
echo "Removing corrupted pip distributions..."
find .venv/lib/python*/site-packages -maxdepth 1 -type d -name "~ip*" -exec rm -rf {} + 2>/dev/null || true

# Reinstall pip
echo
echo "Reinstalling pip..."
source .venv/bin/activate
python3 -m ensurepip --upgrade
python3 -m pip install --upgrade pip

echo
echo "Done! Corrupted distributions removed and pip reinstalled."

