#!/usr/bin/env python3
"""
Main entry point for Media Converter & Organizer
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
src_path = project_root / 'src'
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(src_path))

# Import and run GUI
if __name__ == "__main__":
    from src.media_converter_organizer_gui import main
    main()

