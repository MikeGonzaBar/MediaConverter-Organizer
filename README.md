# Media Converter & Organizer

A comprehensive suite of tools for organizing media files and converting audio, video, and image formats with advanced metadata enhancement. This project combines powerful media processing tools with a unified GUI interface featuring intelligent GPU acceleration and smart conversion modes.

## 🎯 Overview

This project provides:

- **📁 Media Organizer**: Automatically organize photos and videos by date using EXIF/metadata
- **🔄 Media Converter**: Convert audio, video, and image files between formats with GPU acceleration
- **🎵 WAV to FLAC Converter**: Convert WAV files to FLAC with intelligent metadata enhancement
- **🖥️ Unified GUI**: Easy-to-use graphical interface with Simple Mode and Advanced Options
- **🚀 GPU Acceleration**: Smart GPU detection and selection (NVIDIA, AMD, Intel, Apple)
- **🔧 Command Line Tools**: Direct access to all functionality via command line

## 🚀 Quick Start

### 🌍 Cross-Platform Launcher (Recommended)

**Works on Windows, Linux, and macOS!**

1. **Run the unified launcher**:

   ```bash
   python run_gui.py
   ```

   The launcher will:
   - Check Python version
   - Create virtual environment if needed
   - Install dependencies automatically
   - Check for external tools (FFmpeg, Chromaprint)
   - Provide platform-specific installation instructions if needed
   - Launch the GUI

### 🖥️ Platform-Specific Launchers

#### Windows

1. **Run the setup script**:

   ```cmd
   setup.bat
   ```

2. **Launch the GUI**:

   ```cmd
   run_gui.bat
   ```

   Or use the cross-platform launcher:

   ```cmd
   python scripts\run_gui.py
   # or
   python main.py
   ```

#### 🐧 Linux/macOS

1. **Run the setup script**:

   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

2. **Launch the GUI**:

   ```bash
   ./run_gui.sh
   ```

   Or use the cross-platform launcher:

   ```bash
   python3 scripts/run_gui.py
   # or
   python3 main.py
   ```

### 🐍 Manual Setup

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install all dependencies
pip install -r requirements.txt

# Run GUI
python media_converter_organizer_gui.py
```

## 📋 Prerequisites

### Required

- **Python 3.7+** (Python 3.9+ recommended)
- **FFmpeg** (for video metadata and audio processing)
- **tkinter** (usually included with Python, but may need separate install on Linux)

### Optional

- **Chromaprint (fpcalc)** (for audio fingerprinting)
- **Internet connection** (for metadata lookup and fingerprinting)
- **AcoustID API Key** (optional, for audio fingerprinting)
- **Last.fm API Key** (optional, for enhanced metadata)

## 🛠️ Installation

### External Dependencies Installation

#### FFmpeg (Required)

**Windows:**

```bash
winget install ffmpeg
# Or download from: https://ffmpeg.org/download.html
# Add to PATH after installation
```

**macOS:**

```bash
brew install ffmpeg
```

**Linux:**

```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# Fedora
sudo dnf install ffmpeg

# Arch Linux
sudo pacman -S ffmpeg
```

#### Chromaprint (Optional - for audio fingerprinting)

**Windows:**

- Download from: <https://acoustid.org/chromaprint>
- Extract and add `fpcalc.exe` to PATH

**macOS:**

```bash
brew install chromaprint
```

**Linux:**

```bash
# Ubuntu/Debian
sudo apt install chromaprint-tools

# Fedora
sudo dnf install chromaprint-tools

# Arch Linux
sudo pacman -S chromaprint
```

#### tkinter (Required for GUI - usually included)

**Linux (if missing):**

```bash
# Ubuntu/Debian
sudo apt install python3-tk

# Fedora
sudo dnf install python3-tkinter

# Arch Linux
sudo pacman -S tk
```

**Windows/macOS:**

- Usually included with Python installation
- If missing, reinstall Python from [python.org](https://python.org)

### API Keys (Optional)

For enhanced metadata features, get free API keys:

1. **AcoustID API Key**: [Get free key](https://acoustid.org/api-key)
2. **Last.fm API Key**: [Get free key](https://www.last.fm/api)

Create a `.env` file in the project root:

```env
ACOUSTID_API_KEY=your_api_key_here
LASTFM_API_KEY=your_lastfm_key_here
LASTFM_API_SECRET=your_lastfm_secret_here
```

## 📁 Project Structure

```text
MediaConverter-Organizer/
├── 📄 README.md                          # This file
├── 📄 requirements.txt                   # All dependencies
├── 📄 LICENSE                            # Project license
├── 🚀 main.py                            # Main entry point
├── 📁 src/                               # Source code
│   ├── __init__.py                       # Package initialization
│   ├── 🖥️ media_converter_organizer_gui.py   # Main GUI application
│   ├── 🖥️ media_converter_page.py            # Media converter GUI page
│   ├── 🎨 gui_utils.py                       # GUI utilities and styling
│   ├── 🧩 ui_components.py                   # Reusable UI components
│   ├── 🔄 media_converter.py                 # Universal media converter
│   ├── 🖼️ image_organizer.py                 # Image organization tool
│   ├── 🎬 video_organizer.py                 # Video organization tool
│   ├── 🎵 wav_to_flac_converter.py           # WAV to FLAC converter
│   └── 🛠️ dependency_checker.py              # Dependency checking utility
├── 📁 scripts/                           # Launcher and setup scripts
│   ├── 🌍 run_gui.py                     # Cross-platform launcher
│   ├── ⚙️ setup.bat / setup.sh          # Platform-specific setup scripts
│   └── 🚀 run_gui.bat / run_gui.sh       # Platform-specific launcher scripts
├── 📁 docs/                              # Documentation
│   ├── 📄 CROSS_PLATFORM_SETUP.md        # Cross-platform setup guide
│   ├── 📄 TESTING.md                     # Testing guide
│   └── 📄 LASTFM_SETUP.md                # Last.fm API setup guide
└── 📁 assets/                            # Images and icons
    ├── 🖼️ LogoIcon.png                   # Application logo (PNG)
    └── 🖼️ LogoIcon.ico                   # Application icon (ICO)
```

## 🖥️ GUI Application

The unified GUI provides an intuitive interface with two main modes:

### 🎯 Simple Mode (Default)

- **Clean Interface**: Only essential options visible
- **Smart Defaults**: Optimal settings for format-only conversion
- **Auto GPU Selection**: Automatically uses best available GPU
- **Metadata Preservation**: Keeps all original file information
- **Perfect for**: Quick format conversions (MP4→AVI, WAV→MP3, JPG→PNG)

### 🔧 Advanced Mode

- **Full Control**: All quality, codec, and GPU options available
- **Manual GPU Selection**: Choose specific GPU (NVIDIA, AMD, Intel, Apple)
- **Custom Quality Settings**: Fine-tune video/audio/image quality
- **Subtitle Support**: Extract and convert subtitles
- **Perfect for**: Professional workflows and specific requirements

### 📁 Media Organizer Tab

- **Directory Selection**: Browse and select media directories
- **Tool Selection**: Choose Image Organizer, Video Organizer, or Both
- **Configuration Options**: Timeout settings, operation modes
- **Real-time Progress**: Live updates and status messages

### 🔄 Media Converter Tab

#### Input/Output Options

- **Mode Selection**: Directory Mode (batch) or Single File Mode
- **Auto Output Directory**: Automatically sets output to input directory
- **Manual Override**: Option to set custom output directory

#### Media Type Support

- **🎵 Audio**: WAV, FLAC, MP3, AAC, OGG, M4A, WMA
- **🎬 Video**: MP4, AVI, MKV, MOV, WMV, FLV, WebM
- **🖼️ Images**: JPG, JPEG, PNG, BMP, TIFF, GIF, WebP

#### GPU Acceleration

- **Smart Detection**: Automatically detects NVIDIA, AMD, Intel, Apple GPUs
- **Manual Selection**: Choose specific GPU when multiple available
- **Fallback System**: Automatically falls back to CPU if GPU fails
- **Supported Encoders**:
  - NVIDIA: `h264_nvenc`, `hevc_nvenc`, `av1_nvenc`
  - AMD: `h264_amf`, `hevc_amf`
  - Intel: `h264_qsv`, `hevc_qsv`
  - Apple: `h264_videotoolbox`, `hevc_videotoolbox`

#### Quality Settings

- **Audio Quality**: Source, High (320k), Standard (192k), Low (128k)
- **Video Quality**: Source, 8K, 4K, High (1080p), Standard (720p), Low (480p)
- **Image Quality**: High, Standard, Low
- **Framerate**: Source, 60fps, 30fps, 24fps, Custom

#### Advanced Options

- **Codec Selection**: Choose specific video/audio codecs
- **Subtitle Support**: Extract and convert subtitles (SRT, VTT)
- **Metadata Preservation**: Keep or strip metadata
- **Stream Selection**: Choose specific audio/video streams

### 📝 Activity Logs

- **Real-time Logging**: Live progress updates with timestamps
- **Persistent Panel**: Always visible on the right side
- **Color-coded Messages**: Different colors for different message types
- **Scrollable History**: View complete conversion history

## 🔧 Command Line Usage

### Media Organizer

```bash
# Organize images
python image_organizer.py /path/to/images --timeout 600

# Organize videos (check only)
python video_organizer.py /path/to/videos

# Organize videos (dry run)
python video_organizer.py /path/to/videos --dry-run

# Organize videos (actually move files)
python video_organizer.py /path/to/videos --move
```

### Media Converter

```bash
# Convert single audio file
python -c "
from media_converter import MediaConverter
converter = MediaConverter()
converter.convert_single_audio_file('input.wav', 'output_dir', 'mp3')
"

# Convert video with GPU acceleration
python -c "
from media_converter import MediaConverter
converter = MediaConverter()
converter.convert_single_video_file('input.mp4', 'output_dir', 'avi', use_gpu=True)
"
```

### WAV to FLAC Converter

```bash
# Basic conversion
python wav_to_flac_converter.py /path/to/wav

# High quality with metadata
python wav_to_flac_converter.py /path/to/wav --fingerprinting

# Compatibility mode
python wav_to_flac_converter.py /path/to/wav --compatibility

# No metadata lookup
python wav_to_flac_converter.py /path/to/wav --no-metadata
```

## 📦 Dependencies

The unified `requirements.txt` includes all dependencies:

```text
# Media Organizer
Pillow>=9.0.0              # Image EXIF data extraction
ffmpeg-python>=0.2.0       # Video metadata extraction

# Media Converter
ffmpeg-python>=0.2.0       # Video/audio processing
Pillow>=9.0.0              # Image processing

# WAV to FLAC Converter
pydub>=0.25.1              # Audio processing
mutagen>=1.47.0            # FLAC metadata handling
musicbrainzngs>=0.7.1      # MusicBrainz integration
pyacoustid>=1.3.0          # Audio fingerprinting
pylast>=5.0.0              # Last.fm integration
python-dotenv>=1.0.0       # Environment variables

# GUI (tkinter included with Python)
```

## 🌍 Cross-Platform Compatibility

This application is **fully cross-platform** and works on:

- ✅ **Windows** (Windows 10/11)
- ✅ **Linux** (Ubuntu, Debian, Fedora, Arch, etc.)
- ✅ **macOS** (10.14+)

### Platform-Specific Notes

- **Path Handling**: Uses `pathlib.Path` for cross-platform path operations
- **File Separators**: Automatically handles `/` vs `\` differences
- **GPU Support**:
  - Windows/Linux: NVIDIA, AMD, Intel GPUs
  - macOS: Apple Silicon and Intel GPUs via VideoToolbox
- **External Tools**: FFmpeg and Chromaprint must be installed per platform (see installation instructions above)

### Recommended Launcher

Use `run_gui.py` for the best cross-platform experience:

- Automatically detects your platform
- Provides platform-specific installation instructions
- Handles virtual environment setup
- Checks all dependencies

## 🚨 Troubleshooting

### Common Issues

#### ❌ "Python is not installed"

**Solution**: Install Python 3.7+ from [python.org](https://python.org)

#### ❌ "ffmpeg not found"

**Solutions**:

- **Windows**: `winget install ffmpeg`
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg`

#### ❌ "Failed to create virtual environment"

**Solutions**:

- Run `fix_venv.bat` (Windows) to clean and recreate virtual environment
- Run `cleanup_venv.ps1` (Windows PowerShell) for aggressive cleanup
- Ensure write permissions in the current directory
- Try running as administrator (Windows) or with sudo (Linux/macOS)
- Check available disk space

#### ❌ "Failed to install requirements"

**Solutions**:

- Use `run_gui_simple.bat` to bypass virtual environment issues
- Check internet connection
- Update pip: `python -m pip install --upgrade pip`
- Install requirements manually: `pip install -r requirements.txt`

#### ❌ "Cannot load nvcuda.dll" or GPU encoding fails

**Solutions**:

- The app automatically falls back to CPU encoding
- In Advanced Mode, try selecting a different GPU
- Check if your GPU drivers are up to date
- Use "Force CPU encoding" option if needed

#### ❌ "Only VP8/VP9/AV1 and Vorbis/Opus are supported for WebM"

**Solution**: The app automatically uses compatible codecs for WebM (VP9 + Opus)

#### ❌ GUI appears blank

**Solutions**:

- Check if tkinter is installed: `python -c "import tkinter"`
- On Linux: `sudo apt install python3-tk`
- On macOS/Windows: Usually included with Python; if missing, reinstall Python

#### ❌ "Dependencies not found" warnings

**Solutions**:

- Use the cross-platform launcher: `python run_gui.py` - it will show installation instructions
- Check the dependency status: `python dependency_checker.py`
- Install missing dependencies using platform-specific commands (see Prerequisites section)

### Performance Tips

1. **Start with Simple Mode**: Use Simple Mode for basic format conversions
2. **GPU Acceleration**: Enable GPU acceleration for faster video encoding
3. **Batch Processing**: Use Directory Mode for processing multiple files
4. **Monitor Resources**: Ensure sufficient RAM and disk space
5. **Check Logs**: Review activity logs for detailed information

## 🔧 Advanced Usage

### Environment Variables

Create a `.env` file for API keys:

```env
ACOUSTID_API_KEY=your_acoustid_api_key_here
LASTFM_API_KEY=your_lastfm_api_key_here
LASTFM_API_SECRET=your_lastfm_secret_here
```

### GPU Selection

The app automatically detects and uses the best available GPU:

- **NVIDIA**: Uses NVENC encoders for H.264/H.265
- **AMD**: Uses AMF encoders for H.264/H.265  
- **Intel**: Uses QSV encoders for H.264/H.265
- **Apple**: Uses VideoToolbox encoders (macOS only)

### Format Compatibility

The app handles format-specific requirements automatically:

- **WebM**: Automatically uses VP9 video + Opus audio
- **MP4**: Uses H.264 video + AAC audio by default
- **MKV**: Supports H.264, H.265, VP9, AV1 video codecs
- **Audio**: Maintains quality while converting between formats

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

### Development Setup

```bash
# Clone the repository
git clone <repository-url>
cd MediaConverter-Organizer

# Run setup
./setup.sh  # Linux/macOS
# or
setup.bat   # Windows

# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows

# Run GUI
python media_converter_organizer_gui.py
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
