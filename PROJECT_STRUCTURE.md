# Project Structure

This project keeps executable entry points in the root and support scripts in `scripts/`, while all application logic lives under the `src` package.

```text
MediaConverter-Organizer/
|-- main.py
|-- requirements.txt
|-- README.md
|-- PROJECT_STRUCTURE.md
|-- LICENSE
|-- assets/
|   |-- LogoIcon.ico
|   `-- LogoIcon.png
|-- docs/
|   |-- LASTFM_SETUP.md
|   `-- TESTING.md
|-- scripts/
|   |-- fix_pip_corruption.bat
|   |-- fix_pip_corruption.sh
|   |-- run_gui.bat
|   |-- run_gui.py
|   |-- run_gui.sh
|   |-- setup.bat
|   `-- setup.sh
|-- src/
|   |-- __init__.py
|   |-- dependency_checker.py
|   |-- gui_utils.py
|   |-- image_organizer.py
|   |-- media_converter.py
|   |-- media_converter_organizer_gui.py
|   |-- media_converter_page.py
|   |-- ui_components.py
|   |-- video_organizer.py
|   `-- wav_to_flac_converter.py
`-- tests/
    |-- __init__.py
    |-- test_dependency_checker.py
    |-- test_integration_smoke.py
    |-- test_media_converter.py
    |-- test_organizers.py
    `-- test_wav_metadata.py
```

## Directories

`src/` contains the application package:

- `media_converter.py`: audio, video, and image conversion logic.
- `image_organizer.py`: image date extraction and organization.
- `video_organizer.py`: video metadata extraction and organization.
- `wav_to_flac_converter.py`: WAV-to-FLAC conversion and metadata enhancement.
- `media_converter_organizer_gui.py`: main Tk application.
- `media_converter_page.py`: converter page widgets and workflow wiring.
- `ui_components.py`: reusable organizer and WAV page components.
- `gui_utils.py`: styling, icons, window helpers, and shared UI utilities.
- `dependency_checker.py`: optional and required dependency checks.

`scripts/` contains setup and launch helpers:

- `run_gui.py`: cross-platform launcher that can create `.venv`, install requirements, check external tools, and run the GUI.
- `setup.bat` / `setup.sh`: platform setup scripts.
- `run_gui.bat` / `run_gui.sh`: platform launch scripts.
- `fix_pip_corruption.bat` / `fix_pip_corruption.sh`: cleanup helpers for broken local pip metadata.

`docs/` contains task-specific documentation:

- `TESTING.md`: test, compile, diff, smoke, visual, and security audit checks.
- `LASTFM_SETUP.md`: Last.fm API setup for metadata lookup.

`assets/` contains application branding:

- `LogoIcon.png`: logo used inside the GUI.
- `LogoIcon.ico`: Windows icon used by the window and taskbar.

## Running

Use one of these commands from the project root:

```bash
python main.py
python scripts/run_gui.py
```

Windows:

```cmd
scripts\run_gui.bat
```

Linux/macOS:

```bash
./scripts/run_gui.sh
```

## Import Pattern

Application code imports through the `src` package:

```python
from src.media_converter import MediaConverter
from src.gui_utils import WindowManager
from src.ui_components import MediaOrganizerPage
```

`main.py` adds the project root and `src/` directory to `sys.path` before launching the GUI.
