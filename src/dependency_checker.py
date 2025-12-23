"""
Dependency Checker Module
Provides cross-platform dependency checking with helpful installation instructions
"""

import platform
import shutil
from typing import List, Tuple, Optional


class DependencyChecker:
    """Cross-platform dependency checker with installation guidance"""
    
    def __init__(self):
        self.system = platform.system()
        self.missing_required = []
        self.missing_optional = []
    
    def check_ffmpeg(self) -> bool:
        """Check if ffmpeg is available"""
        return shutil.which("ffmpeg") is not None
    
    def check_fpcalc(self) -> bool:
        """Check if fpcalc (Chromaprint) is available"""
        return shutil.which("fpcalc") is not None
    
    def check_python_packages(self) -> Tuple[List[str], List[str]]:
        """Check if required Python packages are installed"""
        required = []
        optional = []
        
        # Required packages
        packages = {
            'PIL': ('Pillow', True),
            'ffmpeg': ('ffmpeg-python', True),
            'mutagen': ('mutagen', False),  # Optional for WAV converter
            'musicbrainzngs': ('musicbrainzngs', False),  # Optional
            'acoustid': ('pyacoustid', False),  # Optional
            'pylast': ('pylast', False),  # Optional
        }
        
        for module, (package_name, is_required) in packages.items():
            try:
                __import__(module)
            except ImportError:
                if is_required:
                    required.append(package_name)
                else:
                    optional.append(package_name)
        
        return required, optional
    
    def get_installation_instructions(self, dependency: str) -> str:
        """Get platform-specific installation instructions"""
        instructions = {
            "ffmpeg": {
                "Windows": "winget install ffmpeg\n  Or download from: https://ffmpeg.org/download.html\n  Add to PATH",
                "Darwin": "brew install ffmpeg",
                "Linux": "Ubuntu/Debian: sudo apt install ffmpeg\n  Fedora: sudo dnf install ffmpeg\n  Arch: sudo pacman -S ffmpeg"
            },
            "fpcalc": {
                "Windows": "Download from: https://acoustid.org/chromaprint\n  Extract and add to PATH",
                "Darwin": "brew install chromaprint",
                "Linux": "Ubuntu/Debian: sudo apt install chromaprint-tools\n  Fedora: sudo dnf install chromaprint-tools\n  Arch: sudo pacman -S chromaprint"
            }
        }
        
        if dependency in instructions:
            platform_instructions = instructions[dependency].get(self.system, "See documentation")
            return f"  {platform_instructions}"
        return "  See documentation for installation instructions"
    
    def check_all(self) -> dict:
        """Check all dependencies and return status"""
        status = {
            'ffmpeg': self.check_ffmpeg(),
            'fpcalc': self.check_fpcalc(),
            'python_packages': self.check_python_packages(),
            'system': self.system
        }
        
        return status
    
    def format_status_message(self, status: dict) -> str:
        """Format dependency status as a readable message"""
        messages = []
        
        # FFmpeg status
        if status['ffmpeg']:
            messages.append("OK: FFmpeg: Available")
        else:
            messages.append("ERROR: FFmpeg: Missing (REQUIRED)")
            messages.append(self.get_installation_instructions("ffmpeg"))
        
        # fpcalc status
        if status['fpcalc']:
            messages.append("OK: Chromaprint (fpcalc): Available")
        else:
            messages.append("WARNING: Chromaprint (fpcalc): Missing (Optional - for audio fingerprinting)")
            messages.append(self.get_installation_instructions("fpcalc"))
        
        # Python packages
        required, optional = status['python_packages']
        if required:
            messages.append(f"ERROR: Missing required Python packages: {', '.join(required)}")
            messages.append(f"  Install with: pip install {' '.join(required)}")
        if optional:
            messages.append(f"WARNING: Missing optional Python packages: {', '.join(optional)}")
            messages.append(f"  Install with: pip install {' '.join(optional)}")
        
        return "\n".join(messages)


def check_dependencies_quick() -> bool:
    """Quick check if critical dependencies are available"""
    checker = DependencyChecker()
    status = checker.check_all()
    
    # Critical: FFmpeg must be available
    if not status['ffmpeg']:
        return False
    
    # Check required Python packages
    required, _ = status['python_packages']
    if required:
        return False
    
    return True


def get_dependency_status() -> dict:
    """Get comprehensive dependency status"""
    checker = DependencyChecker()
    return checker.check_all()


if __name__ == "__main__":
    # Test the dependency checker
    checker = DependencyChecker()
    status = checker.check_all()
    print("Dependency Status:")
    print("=" * 60)
    print(checker.format_status_message(status))

