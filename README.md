# Media Converter & Organizer

Media Converter & Organizer is a desktop toolkit for converting audio, video, and image files, organizing media by date metadata, and converting WAV collections to FLAC with optional MusicBrainz, AcoustID, and Last.fm metadata enhancement.

The GUI is the primary workflow. It includes a media organizer, a universal converter with simple and advanced modes, and a WAV-to-FLAC page. The converter supports GPU-assisted video encoding when FFmpeg exposes compatible NVIDIA, AMD, Intel, or Apple encoders, and falls back to CPU encoding when needed.

## Quick Start

Run these commands from the project root.

### Windows

```cmd
scripts\setup.bat
scripts\run_gui.bat
```

You can also launch directly:

```cmd
python main.py
```

### Linux And macOS

```bash
chmod +x scripts/setup.sh scripts/run_gui.sh
./scripts/setup.sh
./scripts/run_gui.sh
```

You can also launch directly:

```bash
python3 main.py
```

### Cross-Platform Launcher

```bash
python scripts/run_gui.py
```

The launcher can create a `.venv`, install `requirements.txt`, check for FFmpeg and Chromaprint, and start the GUI.

## Requirements

- Python 3.10 or newer.
- FFmpeg in `PATH` for audio/video conversion and video metadata.
- tkinter for the GUI. It is included with standard Windows and macOS Python installers; Linux distributions may package it separately.

Optional:

- Chromaprint / `fpcalc` for audio fingerprinting.
- AcoustID API key for fingerprint lookups.
- Last.fm API key for extra metadata lookup.
- Internet access for MusicBrainz, AcoustID, and Last.fm metadata lookup.

## Install External Tools

### FFmpeg

```bash
# Windows
winget install ffmpeg

# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg

# Fedora
sudo dnf install ffmpeg

# Arch Linux
sudo pacman -S ffmpeg
```

### Chromaprint

```bash
# macOS
brew install chromaprint

# Ubuntu/Debian
sudo apt install chromaprint-tools

# Fedora
sudo dnf install chromaprint-tools

# Arch Linux
sudo pacman -S chromaprint
```

On Windows, download Chromaprint from `https://acoustid.org/chromaprint`, extract it, and add `fpcalc.exe` to `PATH`.

### tkinter On Linux

```bash
# Ubuntu/Debian
sudo apt install python3-tk

# Fedora
sudo dnf install python3-tkinter

# Arch Linux
sudo pacman -S tk
```

## Manual Python Setup

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```

## Optional API Keys

Create a `.env` file in the project root when you want enhanced metadata lookup:

```env
ACOUSTID_API_KEY=your_acoustid_api_key_here
LASTFM_API_KEY=your_lastfm_api_key_here
LASTFM_API_SECRET=your_lastfm_secret_here
```

The Last.fm secret is optional for the current read-only lookup path.

## Main Workflows

### Media Organizer

- Organizes photos and videos by date metadata.
- Supports check, dry-run, and move modes.
- Uses EXIF where available and falls back to filesystem timestamps.
- Supports cancellation from the GUI.

CLI examples:

```bash
python src/image_organizer.py "C:\Media\Photos" --dry-run
python src/video_organizer.py "C:\Media\Videos" --move
```

### Media Converter

- Converts single files or directories.
- Supports audio, video, and image formats.
- Uses case-insensitive extension matching in directory mode.
- Preserves metadata by default where the target format supports it.
- Supports cancellation and FFmpeg timeouts internally.
- Handles WebM codec constraints automatically.
- Keeps overwrite behavior enabled by default.

Supported inputs include:

- Audio: WAV, FLAC, MP3, AAC, OGG, M4A, WMA.
- Video: MP4, AVI, MKV, MOV, WMV, FLV, WebM.
- Images: JPG, JPEG, PNG, BMP, TIFF, GIF, WebP.

Python API example:

```python
from src.media_converter import MediaConverter

converter = MediaConverter()
converter.convert_single_audio_file("input.wav", "output", "mp3")
converter.convert_single_video_file("input.mp4", "output", "mkv", use_gpu=True)
```

### WAV To FLAC Converter

- Converts WAV files to FLAC.
- Copies existing FLAC files into the output set.
- Can skip metadata lookup, use aggressive metadata matching, or enable fingerprinting.
- Embeds metadata when useful fields are found.

CLI examples:

```bash
python src/wav_to_flac_converter.py "C:\Music\WAV"
python src/wav_to_flac_converter.py "C:\Music\WAV" --fingerprinting
python src/wav_to_flac_converter.py "C:\Music\WAV" --no-metadata
```

## GUI Notes

- The app opens directly into the working interface.
- The converter uses a compact simple mode by default and collapsible advanced groups for quality, encoding, streams, subtitles, metadata, and GPU settings.
- The activity log can be collapsed and filtered to focus on errors, warnings, or full progress history.
- Start/stop controls remain visible in each workflow footer.
- On Windows, the app registers its application ID so the taskbar icon matches `assets/LogoIcon.ico`.

## Dependencies And Security Maintenance

`requirements.txt` intentionally uses minimum versions instead of exact pins so patch releases can install without repo changes. The current minimums were reviewed on 2026-05-25:

```text
Pillow>=12.2.0
ffmpeg-python>=0.2.0
pydub>=0.25.1
mutagen>=1.47.0
musicbrainzngs>=0.7.1
pyacoustid>=1.3.1
pylast>=7.0.2
python-dotenv>=1.2.2
```

Security notes:

- Pillow is kept at `>=12.2.0` because earlier 10.3.0 through pre-12.2.0 releases are affected by a high-severity PSD tile extent issue.
- `ffmpeg-python`, `pydub`, `mutagen`, and `musicbrainzngs` have not shipped newer PyPI releases than the listed versions. Keep the external FFmpeg executable updated separately.
- `pyacoustid`, `pylast`, and `python-dotenv` were raised to current releases, which also means the project now documents Python 3.10+.

Useful audit commands:

```bash
python -m pip install --upgrade pip
python -m pip list --outdated
python -m pip check

# Optional vulnerability audit
python -m pip install pip-audit
python -m pip_audit -r requirements.txt
```

Keep FFmpeg and Chromaprint patched through your OS package manager:

```bash
winget upgrade ffmpeg
brew upgrade ffmpeg chromaprint
sudo apt update && sudo apt upgrade
```

## Testing

```bash
python -m unittest discover -s tests -v
python -m compileall -q src tests
git diff --check
```

The unittest suite includes optional FFmpeg smoke tests that skip cleanly when FFmpeg is unavailable.

## GitHub Release Builds

The repository includes a Windows release workflow at `.github/workflows/windows-release.yml`.

It can be run two ways:

- Push a version tag such as `v1.0.0`. The workflow builds the app, uploads the ZIP artifact, and creates a GitHub Release.
- Run "Build Windows EXE" manually from the GitHub Actions tab. Leave `release_tag` empty for an artifact-only build, or provide a tag like `v1.0.0` to create/update a release.

The workflow builds a PyInstaller one-folder app named `MediaConverterOrganizer.exe`, uses `assets/LogoIcon.ico` for the executable icon, includes the `assets/` folder in the bundle, and packages the result as `MediaConverterOrganizer-Windows-<version>.zip`.

FFmpeg and Chromaprint are intentionally not bundled. Install them separately and keep them in `PATH` on the target machine.

## Project Layout

```text
MediaConverter-Organizer/
|-- .github/
|   `-- workflows/
|       `-- windows-release.yml
|-- main.py
|-- requirements.txt
|-- README.md
|-- PROJECT_STRUCTURE.md
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
    |-- test_dependency_checker.py
    |-- test_integration_smoke.py
    |-- test_media_converter.py
    |-- test_organizers.py
    `-- test_wav_metadata.py
```

## Troubleshooting

### FFmpeg Is Missing

Install FFmpeg with your platform package manager, restart the terminal, and confirm:

```bash
ffmpeg -version
```

### GUI Does Not Start

Confirm tkinter is available:

```bash
python -c "import tkinter"
```

On Linux, install the tkinter package for your distribution.

### GPU Encoding Fails

The converter logs the FFmpeg error and retries with CPU encoding when possible. Update GPU drivers, try a different encoder in advanced mode, or force CPU encoding.

### Metadata Lookup Does Not Find Tracks

Confirm your `.env` values are correct, `fpcalc` is available if using fingerprinting, and the machine has internet access. Rare tracks may still fall back to directory-derived metadata.

## Contributing

Keep changes focused, run the tests above, and update documentation when user-visible workflows or dependency requirements change.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
