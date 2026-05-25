"""
Media Converter Module
Handles all media conversion operations (audio, video, image)
"""

import os
import platform
import shutil
import subprocess
import time
from pathlib import Path

from PIL import Image


AUDIO_CODEC_MAP = {
    "mp3": "libmp3lame",
    "flac": "flac",
    "aac": "aac",
    "ogg": "libvorbis",
    "wav": "pcm_s16le",
    "m4a": "aac",
    "wma": "wmav2",
}

AUDIO_QUALITY_BITRATES = {
    "source": None,
    "high": "320k",
    "standard": "192k",
    "low": "128k",
}

LOSSLESS_AUDIO_FORMATS = {"flac", "wav"}

CPU_VIDEO_QUALITY_ARGS = {
    "source": [],
    "8k": ["-vf", "scale=7680:4320", "-crf", "15"],
    "4k": ["-vf", "scale=3840:2160", "-crf", "18"],
    "high": ["-vf", "scale=1920:1080", "-crf", "18"],
    "standard": ["-vf", "scale=1280:720", "-crf", "23"],
    "low": ["-vf", "scale=854:480", "-crf", "28"],
}

GPU_VIDEO_QUALITY_ARGS = {
    "source": [],
    "8k": ["-vf", "scale=7680:4320", "-preset", "fast", "-cq", "15"],
    "4k": ["-vf", "scale=3840:2160", "-preset", "fast", "-cq", "18"],
    "high": ["-vf", "scale=1920:1080", "-preset", "fast", "-cq", "18"],
    "standard": ["-vf", "scale=1280:720", "-preset", "fast", "-cq", "23"],
    "low": ["-vf", "scale=854:480", "-preset", "fast", "-cq", "28"],
}

IMAGE_QUALITY_VALUES = {
    "source": None,
    "high": 95,
    "standard": 80,
    "low": 60,
}

JPEG_OUTPUT_FORMATS = {"jpg", "jpeg"}
IMAGE_RGB_SOURCE_MODES = {"RGBA", "LA", "P"}

GPU_PRIORITY = ("nvidia", "amd", "intel", "apple")
GPU_ENCODER_BY_CODEC = {
    "h264": {
        "nvidia": "h264_nvenc",
        "amd": "h264_amf",
        "intel": "h264_qsv",
        "apple": "h264_videotoolbox",
    },
    "hevc": {
        "nvidia": "hevc_nvenc",
        "amd": "hevc_amf",
        "intel": "hevc_qsv",
        "apple": "hevc_videotoolbox",
    },
    "av1": {
        "nvidia": "av1_nvenc",
    },
}

GPU_ENCODER_CANDIDATES = {
    "nvidia": ("h264_nvenc", "hevc_nvenc", "av1_nvenc"),
    "amd": ("h264_amf", "hevc_amf"),
    "intel": ("h264_qsv", "hevc_qsv"),
    "apple": ("h264_videotoolbox", "hevc_videotoolbox"),
}

GPU_NAMES = {
    "nvidia": "NVIDIA",
    "amd": "AMD",
    "intel": "Intel",
    "apple": "Apple",
}

WEBM_VIDEO_CODEC = "libvpx-vp9"
WEBM_AUDIO_CODEC = "libopus"
CANCELLED_RETURN_CODE = -15
TIMEOUT_RETURN_CODE = -9


class MediaConverter:
    """Handles media conversion operations"""

    def __init__(self, log_callback=None):
        """Initialize converter with optional logging callback"""
        self.log_callback = log_callback
        self.gpu_info = self._detect_gpu_acceleration()
        self.last_run_summary = None
        self._active_process = None
        self._check_dependencies()

    def _check_dependencies(self):
        """Check if required dependencies are available"""
        if not shutil.which("ffmpeg"):
            system = platform.system()
            install_cmd = {
                "Windows": "winget install ffmpeg",
                "Darwin": "brew install ffmpeg",
                "Linux": "sudo apt install ffmpeg  # or: sudo dnf install ffmpeg",
            }.get(system, "See https://ffmpeg.org/download.html")

            self.log_message(
                f"Warning: ffmpeg not found in PATH. Audio and video conversion may not work.\n"
                f"Install with: {install_cmd}",
                "WARNING",
            )

        try:
            from PIL import Image  # noqa: F401
        except ImportError:
            self.log_message(
                "Warning: Pillow (PIL) not found. Image conversion may not work.\n"
                "Install with: pip install Pillow",
                "WARNING",
            )

    def _detect_gpu_acceleration(self):
        """Detect available GPU acceleration options"""
        gpu_info = {
            gpu_type: {"available": False, "encoders": [], "name": GPU_NAMES[gpu_type]}
            for gpu_type in GPU_PRIORITY
        }

        if not shutil.which("ffmpeg"):
            return gpu_info

        try:
            result = subprocess.run(["ffmpeg", "-encoders"], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                encoders_output = result.stdout

                for gpu_type, candidates in GPU_ENCODER_CANDIDATES.items():
                    if gpu_type == "apple" and platform.system() != "Darwin":
                        continue

                    encoders = [encoder for encoder in candidates if encoder in encoders_output]
                    if encoders:
                        gpu_info[gpu_type]["available"] = True
                        gpu_info[gpu_type]["encoders"] = encoders
                        self.log_message(f"{gpu_info[gpu_type]['name']} GPU acceleration detected", "INFO")

                if not any(gpu["available"] for gpu in gpu_info.values()):
                    self.log_message("No GPU acceleration detected, using CPU encoding", "INFO")

        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            self.log_message("Could not detect GPU acceleration, using CPU encoding", "WARNING")

        return gpu_info

    def get_available_gpus(self):
        """Get list of available GPU types"""
        return [
            {
                "type": gpu_type,
                "name": info["name"],
                "encoders": info["encoders"],
            }
            for gpu_type, info in self.gpu_info.items()
            if info["available"]
        ]

    def get_gpu_encoder(self, gpu_type, video_codec="h264"):
        """Get appropriate encoder for GPU type and video codec"""
        if gpu_type not in self.gpu_info or not self.gpu_info[gpu_type]["available"]:
            return None

        encoders = self.gpu_info[gpu_type]["encoders"]
        codec = self._normalize_video_codec(video_codec)
        preferred_encoder = GPU_ENCODER_BY_CODEC.get(codec, {}).get(gpu_type)
        if preferred_encoder in encoders:
            return preferred_encoder

        # Unknown codecs keep the historical fallback; known codecs need a matching encoder.
        if codec not in GPU_ENCODER_BY_CODEC:
            return encoders[0] if encoders else None

        return None

    def get_available_gpu_encoders(self):
        """Get list of available GPU encoders"""
        encoders = []
        for _gpu_type, info in self.gpu_info.items():
            if info["available"]:
                encoders.extend(info["encoders"])
        return encoders

    def get_best_gpu_encoder(self, codec="h264"):
        """Get the best available GPU encoder for a given codec"""
        for gpu_type in GPU_PRIORITY:
            encoder = self.get_gpu_encoder(gpu_type, codec)
            if encoder:
                return encoder
        return None

    def log_message(self, message, level="INFO"):
        """Log message using callback if available"""
        if self.log_callback:
            self.log_callback(message, level)

    @staticmethod
    def _normalize_video_codec(video_codec):
        codec = str(video_codec).lower()
        if codec == "h265":
            return "hevc"
        return codec

    @staticmethod
    def _is_cancelled(cancel_event):
        return bool(cancel_event and cancel_event.is_set())

    @staticmethod
    def _find_files_case_insensitive(input_dir, extension):
        """Find direct child files by extension without case sensitivity."""
        suffix = f".{str(extension).lower().lstrip('.')}"
        return sorted(
            str(path)
            for path in Path(input_dir).iterdir()
            if path.is_file() and path.suffix.lower() == suffix
        )

    @staticmethod
    def _audio_codec_for(output_format):
        return AUDIO_CODEC_MAP.get(str(output_format).lower(), "aac")

    @staticmethod
    def _audio_quality_args(output_format, quality):
        output_format = str(output_format).lower()
        bitrate = AUDIO_QUALITY_BITRATES.get(quality, AUDIO_QUALITY_BITRATES["standard"])
        if bitrate is None or output_format in LOSSLESS_AUDIO_FORMATS:
            return []
        return ["-b:a", bitrate]

    @staticmethod
    def _video_quality_args(quality, uses_gpu):
        quality_map = GPU_VIDEO_QUALITY_ARGS if uses_gpu else CPU_VIDEO_QUALITY_ARGS
        return list(quality_map.get(quality, quality_map["source"]))

    def _video_codec_plan(self, output_format, video_codec, audio_codec, use_gpu, force_cpu, selected_gpu):
        """Resolve output-container overrides and GPU/CPU video encoder selection."""
        output_format = str(output_format).lower()
        if output_format == "webm":
            self.log_message(
                "WebM requires VP8/VP9/AV1 video and Vorbis/Opus audio. Using VP9 (libvpx-vp9) + Opus.",
                "INFO",
            )
            return {
                "actual_video_codec": WEBM_VIDEO_CODEC,
                "cpu_video_codec": WEBM_VIDEO_CODEC,
                "audio_codec": WEBM_AUDIO_CODEC,
                "gpu_encoder": None,
                "uses_gpu": False,
            }

        actual_video_codec = video_codec
        gpu_encoder = None
        if use_gpu and not force_cpu:
            if selected_gpu:
                gpu_encoder = self.get_gpu_encoder(selected_gpu, video_codec)
                if gpu_encoder:
                    actual_video_codec = gpu_encoder
                    gpu_name = self.gpu_info[selected_gpu]["name"]
                    self.log_message(f"Using {gpu_name} GPU acceleration: {gpu_encoder}", "INFO")
                else:
                    self.log_message(
                        f"Selected GPU ({selected_gpu}) not available for {video_codec}, using CPU",
                        "WARNING",
                    )
            else:
                gpu_encoder = self.get_best_gpu_encoder(video_codec)
                if gpu_encoder:
                    actual_video_codec = gpu_encoder
                    self.log_message(f"Using GPU acceleration: {gpu_encoder}", "INFO")
                else:
                    self.log_message("GPU acceleration not available for this codec, using CPU", "INFO")
        else:
            self.log_message("Using CPU encoding", "INFO")

        return {
            "actual_video_codec": actual_video_codec,
            "cpu_video_codec": video_codec,
            "audio_codec": audio_codec,
            "gpu_encoder": gpu_encoder,
            "uses_gpu": bool(gpu_encoder),
        }

    @staticmethod
    def _new_summary(total=0):
        return {"total": total, "success": 0, "failed": 0, "skipped": 0, "cancelled": 0}

    def _set_summary(self, summary):
        self.last_run_summary = summary
        return summary

    @staticmethod
    def _record(summary, outcome):
        if outcome in summary:
            summary[outcome] += 1

    def _log_summary(self, summary, label="Conversion"):
        self.log_message(
            f"{label} summary: {summary['success']} succeeded, {summary['failed']} failed, "
            f"{summary['skipped']} skipped, {summary['cancelled']} cancelled",
            "INFO",
        )

    def _run_ffmpeg(self, cmd, cancel_event=None, timeout_seconds=None):
        """Run ffmpeg with cancellation and timeout support."""
        if self._is_cancelled(cancel_event):
            return subprocess.CompletedProcess(cmd, CANCELLED_RETURN_CODE, "", "Operation cancelled")

        process = None
        stdout = ""
        stderr = ""
        started_at = time.monotonic()

        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self._active_process = process

            while True:
                if self._is_cancelled(cancel_event):
                    stdout, stderr = self._terminate_process(process, "Operation cancelled")
                    return subprocess.CompletedProcess(cmd, CANCELLED_RETURN_CODE, stdout, stderr)

                if timeout_seconds is not None:
                    elapsed = time.monotonic() - started_at
                    if elapsed >= timeout_seconds:
                        stdout, stderr = self._terminate_process(process, f"Timed out after {timeout_seconds} seconds")
                        return subprocess.CompletedProcess(cmd, TIMEOUT_RETURN_CODE, stdout, stderr)
                    wait_timeout = min(0.2, max(0.0, timeout_seconds - elapsed))
                else:
                    wait_timeout = 0.2

                try:
                    stdout, stderr = process.communicate(timeout=wait_timeout)
                    return subprocess.CompletedProcess(cmd, process.returncode, stdout, stderr)
                except subprocess.TimeoutExpired:
                    continue

        except FileNotFoundError as exc:
            return subprocess.CompletedProcess(cmd, 127, stdout, str(exc))
        finally:
            if self._active_process is process:
                self._active_process = None

    @staticmethod
    def _terminate_process(process, reason):
        try:
            process.terminate()
            stdout, stderr = process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()

        stderr = f"{stderr or ''}\n{reason}".strip()
        return stdout or "", stderr

    def stop_active_process(self):
        """Terminate the currently running ffmpeg process, if any."""
        process = self._active_process
        if process and process.poll() is None:
            self._terminate_process(process, "Stop requested")

    def _build_audio_command(
        self,
        input_file,
        output_file,
        output_format,
        quality="standard",
        audio_codec=None,
        preserve_metadata=False,
        overwrite=True,
    ):
        audio_codec = audio_codec or self._audio_codec_for(output_format)
        cmd = ["ffmpeg", "-i", str(input_file), "-c:a", audio_codec]
        cmd.extend(self._audio_quality_args(output_format, quality))
        if preserve_metadata:
            cmd.extend(["-map_metadata", "0"])
        if overwrite:
            cmd.append("-y")
        cmd.append(str(output_file))
        return cmd

    def _build_video_command(
        self,
        input_file,
        output_file,
        actual_video_codec,
        audio_codec,
        quality="source",
        framerate="source",
        uses_gpu=False,
        preserve_metadata=False,
        audio_stream_option=None,
        subtitle_enabled=False,
        subtitle_format="srt",
        subtitle_stream_option="first",
        overwrite=True,
    ):
        cmd = ["ffmpeg", "-i", str(input_file), "-c:v", actual_video_codec, "-c:a", audio_codec]
        cmd.extend(self._video_quality_args(quality, uses_gpu))
        if framerate != "source":
            cmd.extend(["-r", framerate])
        if preserve_metadata:
            cmd.extend(["-map_metadata", "0"])

        if audio_stream_option == "best":
            cmd.extend(["-map", "0:a:0"])
        elif audio_stream_option == "mix":
            cmd.extend(["-filter_complex", "amix=inputs=1", "-map", "0:a"])
        elif audio_stream_option not in (None, "all"):
            cmd.extend(["-map", "0:a:0"])

        if subtitle_enabled and subtitle_stream_option != "all":
            cmd.extend(["-map", "0:s:0", "-c:s", subtitle_format])

        if overwrite:
            cmd.append("-y")
        cmd.append(str(output_file))
        return cmd

    @staticmethod
    def _build_audio_stream_extract_command(input_file, output_file, stream_index, audio_codec):
        return [
            "ffmpeg",
            "-i",
            str(input_file),
            "-map",
            f"0:a:{stream_index}",
            "-c:a",
            audio_codec,
            "-y",
            str(output_file),
        ]

    @staticmethod
    def _build_subtitle_extract_command(input_file, output_file, stream_index, subtitle_format):
        return [
            "ffmpeg",
            "-i",
            str(input_file),
            "-map",
            f"0:s:{stream_index}",
            "-c:s",
            subtitle_format,
            "-y",
            str(output_file),
        ]

    @staticmethod
    def _is_timeout(result):
        return result.returncode == TIMEOUT_RETURN_CODE

    @staticmethod
    def _is_cancel_result(result):
        return result.returncode == CANCELLED_RETURN_CODE

    def _log_result(self, result, display_name, success_message):
        if result.returncode == 0:
            self.log_message(success_message, "SUCCESS")
            return "success"
        if self._is_cancel_result(result):
            self.log_message(f"Cancelled: {display_name}", "WARNING")
            return "cancelled"
        if self._is_timeout(result):
            self.log_message(f"Timed out: {display_name} - {result.stderr}", "ERROR")
            return "failed"

        self.log_message(f"Failed to convert: {display_name} - {result.stderr}", "ERROR")
        return "failed"

    def _convert_audio_file(
        self,
        input_file,
        output_dir,
        output_format,
        quality="standard",
        audio_codec=None,
        preserve_metadata=False,
        cancel_event=None,
        timeout_seconds=None,
    ):
        name = Path(input_file).stem
        output_file = Path(output_dir) / f"{name}.{output_format}"
        display_name = Path(input_file).name
        self.log_message(f"Converting: {display_name}", "INFO")
        cmd = self._build_audio_command(input_file, output_file, output_format, quality, audio_codec, preserve_metadata)
        result = self._run_ffmpeg(cmd, cancel_event=cancel_event, timeout_seconds=timeout_seconds)
        return self._log_result(result, display_name, f"Successfully converted: {display_name}")

    def convert_audio_files(
        self,
        input_dir,
        output_dir,
        input_format,
        output_format,
        quality="standard",
        audio_codec=None,
        preserve_metadata=False,
        *,
        cancel_event=None,
        timeout_seconds=None,
    ):
        """Convert audio files using ffmpeg"""
        summary = self._set_summary(self._new_summary())
        if not os.path.exists(input_dir):
            self.log_message(f"Input directory does not exist: {input_dir}", "ERROR")
            return summary

        if input_format == output_format:
            self.log_message("Input and output formats are the same. No conversion needed.", "WARNING")
            summary["skipped"] += 1
            return summary

        audio_files = self._find_files_case_insensitive(input_dir, input_format)
        summary["total"] = len(audio_files)
        if not audio_files:
            self.log_message(f"No {str(input_format).upper()} files found in input directory", "WARNING")
            return summary

        os.makedirs(output_dir, exist_ok=True)

        for audio_file in audio_files:
            if self._is_cancelled(cancel_event):
                self.log_message("Audio conversion cancelled before next file", "WARNING")
                summary["cancelled"] += 1
                break

            outcome = self._convert_audio_file(
                audio_file,
                output_dir,
                output_format,
                quality=quality,
                audio_codec=audio_codec,
                preserve_metadata=preserve_metadata,
                cancel_event=cancel_event,
                timeout_seconds=timeout_seconds,
            )
            self._record(summary, outcome)
            if outcome == "cancelled":
                break

        self._log_summary(summary, "Audio conversion")
        return summary

    def convert_single_audio_file(
        self,
        input_file,
        output_dir,
        output_format,
        quality="standard",
        audio_codec=None,
        preserve_metadata=False,
        *,
        cancel_event=None,
        timeout_seconds=None,
    ):
        """Convert a single audio file using ffmpeg."""
        summary = self._set_summary(self._new_summary(total=1))
        if not os.path.exists(input_file):
            self.log_message(f"Input file does not exist: {input_file}", "ERROR")
            summary["failed"] += 1
            return summary

        if self._is_cancelled(cancel_event):
            self.log_message("Audio conversion cancelled before starting", "WARNING")
            summary["cancelled"] += 1
            return summary

        os.makedirs(output_dir, exist_ok=True)
        outcome = self._convert_audio_file(
            input_file,
            output_dir,
            output_format,
            quality=quality,
            audio_codec=audio_codec,
            preserve_metadata=preserve_metadata,
            cancel_event=cancel_event,
            timeout_seconds=timeout_seconds,
        )
        self._record(summary, outcome)
        return summary

    def _extract_video_side_streams(
        self,
        input_file,
        output_dir,
        name,
        output_format,
        audio_codec,
        audio_stream_option,
        subtitle_enabled,
        subtitle_format,
        subtitle_stream_option,
        cancel_event,
        timeout_seconds,
    ):
        if audio_stream_option == "all":
            for i in range(10):
                if self._is_cancelled(cancel_event):
                    return "cancelled"
                audio_output = Path(output_dir) / f"{name}_audio_{i}.{output_format}"
                audio_cmd = self._build_audio_stream_extract_command(input_file, audio_output, i, audio_codec)
                result = self._run_ffmpeg(audio_cmd, cancel_event=cancel_event, timeout_seconds=timeout_seconds)
                if self._is_cancel_result(result):
                    return "cancelled"
                if result.returncode != 0:
                    break

        if subtitle_enabled and subtitle_stream_option == "all":
            for i in range(10):
                if self._is_cancelled(cancel_event):
                    return "cancelled"
                subtitle_output = Path(output_dir) / f"{name}_subtitle_{i}.{subtitle_format}"
                subtitle_cmd = self._build_subtitle_extract_command(input_file, subtitle_output, i, subtitle_format)
                result = self._run_ffmpeg(subtitle_cmd, cancel_event=cancel_event, timeout_seconds=timeout_seconds)
                if self._is_cancel_result(result):
                    return "cancelled"
                if result.returncode != 0:
                    break

        return None

    def _convert_video_file(
        self,
        input_file,
        output_dir,
        output_format,
        codec_plan,
        quality="source",
        framerate="source",
        preserve_metadata=False,
        audio_stream_option=None,
        subtitle_enabled=False,
        subtitle_format="srt",
        subtitle_stream_option="first",
        cancel_event=None,
        timeout_seconds=None,
        retry_gpu_with_cpu=False,
    ):
        input_path = Path(input_file)
        name = input_path.stem
        output_file = Path(output_dir) / f"{name}.{output_format}"
        display_name = input_path.name
        self.log_message(f"Converting: {display_name}", "INFO")

        stream_outcome = self._extract_video_side_streams(
            input_file,
            output_dir,
            name,
            output_format,
            codec_plan["audio_codec"],
            audio_stream_option,
            subtitle_enabled,
            subtitle_format,
            subtitle_stream_option,
            cancel_event,
            timeout_seconds,
        )
        if stream_outcome == "cancelled":
            self.log_message(f"Cancelled: {display_name}", "WARNING")
            return "cancelled"

        cmd = self._build_video_command(
            input_file,
            output_file,
            codec_plan["actual_video_codec"],
            codec_plan["audio_codec"],
            quality=quality,
            framerate=framerate,
            uses_gpu=codec_plan["uses_gpu"],
            preserve_metadata=preserve_metadata,
            audio_stream_option=audio_stream_option,
            subtitle_enabled=subtitle_enabled,
            subtitle_format=subtitle_format,
            subtitle_stream_option=subtitle_stream_option,
        )

        result = self._run_ffmpeg(cmd, cancel_event=cancel_event, timeout_seconds=timeout_seconds)
        if result.returncode == 0:
            self.log_message(f"Successfully converted: {display_name}", "SUCCESS")
            return "success"

        if retry_gpu_with_cpu and codec_plan["gpu_encoder"] and not self._is_cancel_result(result):
            self.log_message(f"GPU encoding failed, falling back to CPU encoding: {result.stderr}", "WARNING")
            cpu_cmd = self._build_video_command(
                input_file,
                output_file,
                codec_plan["cpu_video_codec"],
                codec_plan["audio_codec"],
                quality=quality,
                framerate=framerate,
                uses_gpu=False,
                preserve_metadata=preserve_metadata,
            )
            cpu_result = self._run_ffmpeg(cpu_cmd, cancel_event=cancel_event, timeout_seconds=timeout_seconds)
            if cpu_result.returncode == 0:
                self.log_message(f"Successfully converted with CPU fallback: {name}", "SUCCESS")
                return "success"
            if self._is_cancel_result(cpu_result):
                self.log_message(f"Cancelled: {display_name}", "WARNING")
                return "cancelled"
            if self._is_timeout(cpu_result):
                self.log_message(f"CPU fallback timed out: {name} - {cpu_result.stderr}", "ERROR")
                return "failed"
            self.log_message(f"CPU fallback also failed: {name} - {cpu_result.stderr}", "ERROR")
            return "failed"

        return self._log_result(result, display_name, f"Successfully converted: {display_name}")

    def convert_video_files(
        self,
        input_dir,
        output_dir,
        input_format,
        output_format,
        quality="source",
        framerate="source",
        video_codec="h264",
        audio_codec="aac",
        audio_stream_option="first",
        subtitle_enabled=False,
        subtitle_format="srt",
        subtitle_stream_option="first",
        preserve_metadata=False,
        use_gpu=True,
        force_cpu=False,
        selected_gpu=None,
        *,
        cancel_event=None,
        timeout_seconds=None,
    ):
        """Convert video files using ffmpeg"""
        summary = self._set_summary(self._new_summary())
        if not os.path.exists(input_dir):
            self.log_message(f"Input directory does not exist: {input_dir}", "ERROR")
            return summary

        if input_format == output_format:
            self.log_message("Input and output formats are the same. No conversion needed.", "WARNING")
            summary["skipped"] += 1
            return summary

        video_files = self._find_files_case_insensitive(input_dir, input_format)
        summary["total"] = len(video_files)
        if not video_files:
            self.log_message(f"No {str(input_format).upper()} files found in input directory", "WARNING")
            return summary

        os.makedirs(output_dir, exist_ok=True)
        codec_plan = self._video_codec_plan(output_format, video_codec, audio_codec, use_gpu, force_cpu, selected_gpu)

        for video_file in video_files:
            if self._is_cancelled(cancel_event):
                self.log_message("Video conversion cancelled before next file", "WARNING")
                summary["cancelled"] += 1
                break

            outcome = self._convert_video_file(
                video_file,
                output_dir,
                output_format,
                codec_plan,
                quality=quality,
                framerate=framerate,
                preserve_metadata=preserve_metadata,
                audio_stream_option=audio_stream_option,
                subtitle_enabled=subtitle_enabled,
                subtitle_format=subtitle_format,
                subtitle_stream_option=subtitle_stream_option,
                cancel_event=cancel_event,
                timeout_seconds=timeout_seconds,
                retry_gpu_with_cpu=False,
            )
            self._record(summary, outcome)
            if outcome == "cancelled":
                break

        self._log_summary(summary, "Video conversion")
        return summary

    def convert_single_video_file(
        self,
        input_file,
        output_dir,
        output_format,
        quality="source",
        framerate="source",
        video_codec="h264",
        audio_codec="aac",
        preserve_metadata=False,
        use_gpu=True,
        force_cpu=False,
        selected_gpu=None,
        *,
        cancel_event=None,
        timeout_seconds=None,
    ):
        """Convert a single video file using ffmpeg."""
        summary = self._set_summary(self._new_summary(total=1))
        if not os.path.exists(input_file):
            self.log_message(f"Input file does not exist: {input_file}", "ERROR")
            summary["failed"] += 1
            return summary

        if self._is_cancelled(cancel_event):
            self.log_message("Video conversion cancelled before starting", "WARNING")
            summary["cancelled"] += 1
            return summary

        os.makedirs(output_dir, exist_ok=True)
        codec_plan = self._video_codec_plan(output_format, video_codec, audio_codec, use_gpu, force_cpu, selected_gpu)
        outcome = self._convert_video_file(
            input_file,
            output_dir,
            output_format,
            codec_plan,
            quality=quality,
            framerate=framerate,
            preserve_metadata=preserve_metadata,
            cancel_event=cancel_event,
            timeout_seconds=timeout_seconds,
            retry_gpu_with_cpu=not force_cpu,
        )
        self._record(summary, outcome)
        return summary

    def _save_image_file(self, input_file, output_file, output_format, quality):
        quality_value = IMAGE_QUALITY_VALUES.get(quality, IMAGE_QUALITY_VALUES["standard"])
        output_format = str(output_format).lower()
        with Image.open(input_file) as img:
            if output_format in JPEG_OUTPUT_FORMATS and img.mode in IMAGE_RGB_SOURCE_MODES:
                img = img.convert("RGB")
            if output_format in JPEG_OUTPUT_FORMATS:
                if quality_value is not None:
                    img.save(output_file, quality=quality_value, optimize=True)
                else:
                    img.save(output_file, optimize=True)
            else:
                img.save(output_file)

    def _convert_image_file(self, input_file, output_dir, output_format, quality="standard"):
        name = Path(input_file).stem
        output_file = Path(output_dir) / f"{name}.{output_format}"
        display_name = Path(input_file).name
        self.log_message(f"Converting: {display_name}", "INFO")

        try:
            self._save_image_file(input_file, output_file, output_format, quality)
            self.log_message(f"Successfully converted: {display_name}", "SUCCESS")
            return "success"
        except Exception as e:
            self.log_message(f"Failed to convert: {display_name} - {str(e)}", "ERROR")
            return "failed"

    def convert_image_files(
        self,
        input_dir,
        output_dir,
        input_format,
        output_format,
        quality="standard",
        *,
        cancel_event=None,
        timeout_seconds=None,
    ):
        """Convert image files using PIL"""
        del timeout_seconds  # PIL conversion is synchronous; keep the interface aligned with media converters.
        summary = self._set_summary(self._new_summary())
        if not os.path.exists(input_dir):
            self.log_message(f"Input directory does not exist: {input_dir}", "ERROR")
            return summary

        if input_format == output_format:
            self.log_message("Input and output formats are the same. No conversion needed.", "WARNING")
            summary["skipped"] += 1
            return summary

        image_files = self._find_files_case_insensitive(input_dir, input_format)
        summary["total"] = len(image_files)
        if not image_files:
            self.log_message(f"No {str(input_format).upper()} files found in input directory", "WARNING")
            return summary

        os.makedirs(output_dir, exist_ok=True)

        for image_file in image_files:
            if self._is_cancelled(cancel_event):
                self.log_message("Image conversion cancelled before next file", "WARNING")
                summary["cancelled"] += 1
                break

            outcome = self._convert_image_file(image_file, output_dir, output_format, quality)
            self._record(summary, outcome)

        self._log_summary(summary, "Image conversion")
        return summary

    def convert_single_image_file(
        self,
        input_file,
        output_dir,
        output_format,
        quality="standard",
        *,
        cancel_event=None,
        timeout_seconds=None,
    ):
        """Convert a single image file using PIL."""
        del timeout_seconds
        summary = self._set_summary(self._new_summary(total=1))
        if not os.path.exists(input_file):
            self.log_message(f"Input file does not exist: {input_file}", "ERROR")
            summary["failed"] += 1
            return summary

        if self._is_cancelled(cancel_event):
            self.log_message("Image conversion cancelled before starting", "WARNING")
            summary["cancelled"] += 1
            return summary

        os.makedirs(output_dir, exist_ok=True)
        outcome = self._convert_image_file(input_file, output_dir, output_format, quality)
        self._record(summary, outcome)
        return summary
