import threading
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from src import media_converter


def make_converter(gpu_info=None):
    logs = []
    converter = media_converter.MediaConverter.__new__(media_converter.MediaConverter)
    converter.log_callback = lambda message, level="INFO": logs.append((level, message))
    converter.gpu_info = gpu_info or {
        "nvidia": {"available": False, "encoders": [], "name": "NVIDIA"},
        "amd": {"available": False, "encoders": [], "name": "AMD"},
        "intel": {"available": False, "encoders": [], "name": "Intel"},
        "apple": {"available": False, "encoders": [], "name": "Apple"},
    }
    converter._active_process = None
    converter.last_run_summary = None
    return converter, logs


def ffmpeg_result(returncode=0, stderr=""):
    return media_converter.subprocess.CompletedProcess(["ffmpeg"], returncode, "", stderr)


class MediaConverterCommandTests(unittest.TestCase):
    def test_single_audio_preserves_metadata_before_output_file(self):
        converter, _ = make_converter()
        with tempfile.TemporaryDirectory() as tmp:
            input_file = Path(tmp) / "song.wav"
            output_dir = Path(tmp) / "out"
            input_file.write_bytes(b"fake wav")

            with patch.object(converter, "_run_ffmpeg", return_value=ffmpeg_result()) as run:
                converter.convert_single_audio_file(
                    str(input_file),
                    str(output_dir),
                    "mp3",
                    quality="high",
                    preserve_metadata=True,
                )

            cmd = run.call_args.args[0]
            output_file = str(output_dir / "song.mp3")
            self.assertEqual(cmd[-1], output_file)
            self.assertLess(cmd.index("-map_metadata"), cmd.index(output_file))
            self.assertLess(cmd.index("-b:a"), cmd.index(output_file))

    def test_directory_audio_preserves_metadata_before_output_file(self):
        converter, _ = make_converter()
        with tempfile.TemporaryDirectory() as tmp:
            input_dir = Path(tmp) / "in"
            output_dir = Path(tmp) / "out"
            input_dir.mkdir()
            (input_dir / "track.WAV").write_bytes(b"fake wav")

            with patch.object(converter, "_run_ffmpeg", return_value=ffmpeg_result()) as run:
                summary = converter.convert_audio_files(
                    str(input_dir),
                    str(output_dir),
                    "wav",
                    "mp3",
                    quality="low",
                    preserve_metadata=True,
                )

            cmd = run.call_args.args[0]
            output_file = str(output_dir / "track.mp3")
            self.assertEqual(cmd[-1], output_file)
            self.assertEqual(cmd[cmd.index("-b:a") + 1], "128k")
            self.assertLess(cmd.index("-map_metadata"), cmd.index(output_file))
            self.assertEqual(summary["success"], 1)

    def test_directory_video_places_maps_subtitles_and_metadata_before_output_file(self):
        converter, _ = make_converter()
        with tempfile.TemporaryDirectory() as tmp:
            input_dir = Path(tmp) / "in"
            output_dir = Path(tmp) / "out"
            input_dir.mkdir()
            video = input_dir / "clip.mp4"
            video.write_bytes(b"fake video")

            with patch.object(converter, "_run_ffmpeg", return_value=ffmpeg_result()) as run:
                converter.convert_video_files(
                    str(input_dir),
                    str(output_dir),
                    "mp4",
                    "mkv",
                    audio_stream_option="first",
                    subtitle_enabled=True,
                    subtitle_format="srt",
                    preserve_metadata=True,
                    use_gpu=False,
                )

            cmd = run.call_args.args[0]
            output_file = str(output_dir / "clip.mkv")
            self.assertEqual(cmd[-1], output_file)
            for option in ("-map", "-c:s", "-map_metadata"):
                self.assertLess(cmd.index(option), cmd.index(output_file))

    def test_selected_h265_gpu_uses_hevc_encoder(self):
        converter, _ = make_converter(
            {
                "nvidia": {"available": True, "encoders": ["h264_nvenc", "hevc_nvenc"], "name": "NVIDIA"},
                "amd": {"available": False, "encoders": [], "name": "AMD"},
                "intel": {"available": False, "encoders": [], "name": "Intel"},
                "apple": {"available": False, "encoders": [], "name": "Apple"},
            }
        )

        self.assertEqual(converter.get_gpu_encoder("nvidia", "h265"), "hevc_nvenc")

    def test_single_video_gpu_fallback_rebuilds_cpu_quality_arguments(self):
        converter, logs = make_converter(
            {
                "nvidia": {"available": True, "encoders": ["h264_nvenc"], "name": "NVIDIA"},
                "amd": {"available": False, "encoders": [], "name": "AMD"},
                "intel": {"available": False, "encoders": [], "name": "Intel"},
                "apple": {"available": False, "encoders": [], "name": "Apple"},
            }
        )
        with tempfile.TemporaryDirectory() as tmp:
            input_file = Path(tmp) / "clip.mp4"
            output_dir = Path(tmp) / "out"
            input_file.write_bytes(b"fake video")

            results = [
                SimpleNamespace(returncode=1, stderr="gpu failed"),
                SimpleNamespace(returncode=0, stderr=""),
            ]
            with patch.object(converter, "_run_ffmpeg", side_effect=results) as run:
                converter.convert_single_video_file(
                    str(input_file),
                    str(output_dir),
                    "mp4",
                    quality="high",
                    use_gpu=True,
                    force_cpu=False,
                )

            first_cmd = run.call_args_list[0].args[0]
            fallback_cmd = run.call_args_list[1].args[0]
            self.assertIn("-cq", first_cmd)
            self.assertIn("-crf", fallback_cmd)
            self.assertNotIn("-cq", fallback_cmd)
            self.assertEqual(fallback_cmd[fallback_cmd.index("-c:v") + 1], "h264")
            self.assertTrue(any(level == "SUCCESS" for level, _ in logs))

    def test_webm_single_video_forces_vp9_opus_and_disables_gpu(self):
        converter, _ = make_converter(
            {
                "nvidia": {"available": True, "encoders": ["h264_nvenc"], "name": "NVIDIA"},
                "amd": {"available": False, "encoders": [], "name": "AMD"},
                "intel": {"available": False, "encoders": [], "name": "Intel"},
                "apple": {"available": False, "encoders": [], "name": "Apple"},
            }
        )
        with tempfile.TemporaryDirectory() as tmp:
            input_file = Path(tmp) / "clip.mp4"
            output_dir = Path(tmp) / "out"
            input_file.write_bytes(b"fake video")

            with patch.object(converter, "_run_ffmpeg", return_value=ffmpeg_result()) as run:
                converter.convert_single_video_file(str(input_file), str(output_dir), "webm")

            cmd = run.call_args.args[0]
            self.assertEqual(cmd[cmd.index("-c:v") + 1], "libvpx-vp9")
            self.assertEqual(cmd[cmd.index("-c:a") + 1], "libopus")
            self.assertNotIn("h264_nvenc", cmd)

    def test_known_gpu_codec_without_matching_encoder_returns_none(self):
        converter, _ = make_converter(
            {
                "nvidia": {"available": True, "encoders": ["h264_nvenc"], "name": "NVIDIA"},
                "amd": {"available": False, "encoders": [], "name": "AMD"},
                "intel": {"available": False, "encoders": [], "name": "Intel"},
                "apple": {"available": False, "encoders": [], "name": "Apple"},
            }
        )

        self.assertIsNone(converter.get_gpu_encoder("nvidia", "hevc"))

    def test_directory_video_matches_input_extension_case_insensitively(self):
        converter, _ = make_converter()
        with tempfile.TemporaryDirectory() as tmp:
            input_dir = Path(tmp) / "in"
            output_dir = Path(tmp) / "out"
            input_dir.mkdir()
            (input_dir / "CLIP.MP4").write_bytes(b"fake video")

            with patch.object(converter, "_run_ffmpeg", return_value=ffmpeg_result()) as run:
                summary = converter.convert_video_files(
                    str(input_dir),
                    str(output_dir),
                    "mp4",
                    "mkv",
                    use_gpu=False,
                )

            self.assertEqual(run.call_count, 1)
            self.assertEqual(summary["success"], 1)

    def test_cancelled_audio_directory_stops_before_running_ffmpeg(self):
        converter, logs = make_converter()
        cancel_event = threading.Event()
        cancel_event.set()
        with tempfile.TemporaryDirectory() as tmp:
            input_dir = Path(tmp) / "in"
            output_dir = Path(tmp) / "out"
            input_dir.mkdir()
            (input_dir / "track.wav").write_bytes(b"fake wav")

            with patch.object(converter, "_run_ffmpeg", return_value=ffmpeg_result()) as run:
                summary = converter.convert_audio_files(
                    str(input_dir),
                    str(output_dir),
                    "wav",
                    "mp3",
                    cancel_event=cancel_event,
                )

            run.assert_not_called()
            self.assertEqual(summary["cancelled"], 1)
            self.assertTrue(any("cancelled" in message.lower() for _, message in logs))

    def test_run_ffmpeg_returns_cancelled_without_starting_process_when_event_is_set(self):
        converter, _ = make_converter()
        cancel_event = threading.Event()
        cancel_event.set()

        with patch.object(media_converter.subprocess, "Popen") as popen:
            result = converter._run_ffmpeg(["ffmpeg", "-version"], cancel_event=cancel_event)

        popen.assert_not_called()
        self.assertEqual(result.returncode, media_converter.CANCELLED_RETURN_CODE)

    def test_run_ffmpeg_times_out_and_terminates_process(self):
        converter, _ = make_converter()

        class SlowProcess:
            returncode = None

            def __init__(self):
                self.terminated = False
                self.killed = False

            def communicate(self, timeout=None):
                if self.terminated:
                    self.returncode = media_converter.TIMEOUT_RETURN_CODE
                    return "", "terminated"
                raise media_converter.subprocess.TimeoutExpired(["ffmpeg"], timeout)

            def terminate(self):
                self.terminated = True

            def kill(self):
                self.killed = True

        process = SlowProcess()
        with patch.object(media_converter.subprocess, "Popen", return_value=process):
            result = converter._run_ffmpeg(["ffmpeg", "-i", "input"], timeout_seconds=0)

        self.assertEqual(result.returncode, media_converter.TIMEOUT_RETURN_CODE)
        self.assertTrue(process.terminated)

    def test_single_image_rgba_to_jpeg_converts_to_rgb(self):
        converter, _ = make_converter()
        with tempfile.TemporaryDirectory() as tmp:
            from PIL import Image

            input_file = Path(tmp) / "transparent.png"
            output_dir = Path(tmp) / "out"
            Image.new("RGBA", (2, 2), (255, 0, 0, 128)).save(input_file)

            converter.convert_single_image_file(str(input_file), str(output_dir), "jpg", quality="source")

            output_file = output_dir / "transparent.jpg"
            self.assertTrue(output_file.exists())
            with Image.open(output_file) as img:
                self.assertEqual(img.mode, "RGB")

    def test_single_image_missing_input_logs_error_and_skips_output_dir(self):
        converter, logs = make_converter()
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "out"

            converter.convert_single_image_file(str(Path(tmp) / "missing.png"), str(output_dir), "jpg")

            self.assertFalse(output_dir.exists())
            self.assertTrue(any(level == "ERROR" and "does not exist" in message for level, message in logs))


if __name__ == "__main__":
    unittest.main()
