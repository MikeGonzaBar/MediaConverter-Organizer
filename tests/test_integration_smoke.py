import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from src.media_converter import MediaConverter


@unittest.skipIf(shutil.which("ffmpeg") is None, "ffmpeg is not available")
class OptionalFfmpegSmokeTests(unittest.TestCase):
    def test_tiny_generated_wav_can_convert_to_flac(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            input_file = root / "tiny.wav"
            output_dir = root / "out"

            subprocess.run(
                [
                    "ffmpeg",
                    "-f",
                    "lavfi",
                    "-i",
                    "anullsrc=r=8000:cl=mono",
                    "-t",
                    "0.1",
                    "-y",
                    str(input_file),
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            converter = MediaConverter.__new__(MediaConverter)
            converter.log_callback = lambda *_args: None
            converter.gpu_info = {
                "nvidia": {"available": False, "encoders": [], "name": "NVIDIA"},
                "amd": {"available": False, "encoders": [], "name": "AMD"},
                "intel": {"available": False, "encoders": [], "name": "Intel"},
                "apple": {"available": False, "encoders": [], "name": "Apple"},
            }
            converter._active_process = None

            summary = converter.convert_single_audio_file(str(input_file), str(output_dir), "flac")

            self.assertEqual(summary["success"], 1)
            self.assertTrue((output_dir / "tiny.flac").exists())


if __name__ == "__main__":
    unittest.main()
