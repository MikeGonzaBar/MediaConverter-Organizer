# Project Structure

This document describes the organized folder structure of the Media Converter & Organizer project.

## 📁 Folder Organization

```
MediaConverter-Organizer/
├── src/              # All Python source code
├── scripts/          # Launcher and setup scripts
├── docs/             # Documentation files
├── assets/           # Images, icons, and other assets
└── [root files]      # Configuration and entry points
```

## 📂 Directory Details

### `src/` - Source Code

Contains all Python modules:

- **Core modules**: `media_converter.py`, `image_organizer.py`, `video_organizer.py`, `wav_to_flac_converter.py`
- **GUI modules**: `media_converter_organizer_gui.py`, `media_converter_page.py`, `ui_components.py`, `gui_utils.py`
- **Utilities**: `dependency_checker.py`
- **Package file**: `__init__.py` (makes src a Python package)

### `scripts/` - Launcher Scripts

Contains all launcher and setup scripts:

- **Cross-platform**: `run_gui.py` (works on Windows, Linux, macOS)
- **Windows**: `setup.bat`, `run_gui.bat`
- **Linux/macOS**: `setup.sh`, `run_gui.sh`

### `docs/` - Documentation

Contains additional documentation:

- `CROSS_PLATFORM_SETUP.md` - Cross-platform setup guide
- `TESTING.md` - Testing documentation
- `LASTFM_SETUP.md` - Last.fm API setup guide

### `assets/` - Assets

Contains images and icons:

- `LogoIcon.png` - Application logo (PNG format)
- `LogoIcon.ico` - Application icon (ICO format, auto-generated)

### Root Files

- `README.md` - Main documentation (stays in root per convention)
- `requirements.txt` - Python dependencies (stays in root per convention)
- `LICENSE` - Project license
- `main.py` - Main entry point for the application

## 🔄 Import Structure

All imports use the `src.` prefix:

```python
from src.media_converter import MediaConverter
from src.gui_utils import WindowManager
from src.ui_components import MediaOrganizerPage
```

## 🚀 Running the Application

### Option 1: Main Entry Point (Recommended)

```bash
python main.py
```

### Option 2: Cross-Platform Launcher

```bash
python scripts/run_gui.py
```

### Option 3: Platform-Specific Scripts

- **Windows**: `scripts\run_gui.bat`
- **Linux/macOS**: `./scripts/run_gui.sh`

## 📝 Notes

- The `src/` folder is a Python package (contains `__init__.py`)
- Asset paths are resolved relative to the project root
- All scripts assume they're run from the project root directory
- The `main.py` file handles path setup automatically
