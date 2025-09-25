"""
Media Converter Module
Handles all media conversion operations (audio, video, image)
"""

import os
import glob
import subprocess
import shutil
import platform
from PIL import Image


class MediaConverter:
    """Handles media conversion operations"""
    
    def __init__(self, log_callback=None):
        """Initialize converter with optional logging callback"""
        self.log_callback = log_callback
        self.gpu_info = self._detect_gpu_acceleration()
        self._check_dependencies()
    
    def _check_dependencies(self):
        """Check if required dependencies are available"""
        # Check if ffmpeg is available
        if not shutil.which("ffmpeg"):
            self.log_message("Warning: ffmpeg not found in PATH. Audio and video conversion may not work.", "WARNING")
        
        # Check if PIL is available
        try:
            from PIL import Image
        except ImportError:
            self.log_message("Warning: Pillow (PIL) not found. Image conversion may not work.", "WARNING")
    
    def _detect_gpu_acceleration(self):
        """Detect available GPU acceleration options"""
        gpu_info = {
            'nvidia': {'available': False, 'encoders': [], 'name': 'NVIDIA'},
            'amd': {'available': False, 'encoders': [], 'name': 'AMD'},
            'intel': {'available': False, 'encoders': [], 'name': 'Intel'},
            'apple': {'available': False, 'encoders': [], 'name': 'Apple'}
        }
        
        if not shutil.which("ffmpeg"):
            return gpu_info
        
        try:
            # Get ffmpeg encoder list
            result = subprocess.run(['ffmpeg', '-encoders'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                encoders_output = result.stdout
                
                # Check for NVIDIA encoders
                if 'h264_nvenc' in encoders_output:
                    gpu_info['nvidia']['available'] = True
                    gpu_info['nvidia']['encoders'] = ['h264_nvenc', 'hevc_nvenc', 'av1_nvenc']
                    self.log_message("NVIDIA GPU acceleration detected", "INFO")
                
                # Check for AMD encoders
                if 'h264_amf' in encoders_output:
                    gpu_info['amd']['available'] = True
                    gpu_info['amd']['encoders'] = ['h264_amf', 'hevc_amf']
                    self.log_message("AMD GPU acceleration detected", "INFO")
                
                # Check for Intel encoders
                if 'h264_qsv' in encoders_output:
                    gpu_info['intel']['available'] = True
                    gpu_info['intel']['encoders'] = ['h264_qsv', 'hevc_qsv']
                    self.log_message("Intel GPU acceleration detected", "INFO")
                
                # Check for Apple encoders (macOS)
                if platform.system() == 'Darwin' and 'h264_videotoolbox' in encoders_output:
                    gpu_info['apple']['available'] = True
                    gpu_info['apple']['encoders'] = ['h264_videotoolbox', 'hevc_videotoolbox']
                    self.log_message("Apple GPU acceleration detected", "INFO")
                
                if not any(gpu['available'] for gpu in gpu_info.values()):
                    self.log_message("No GPU acceleration detected, using CPU encoding", "INFO")
                    
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            self.log_message("Could not detect GPU acceleration, using CPU encoding", "WARNING")
        
        return gpu_info
    
    def get_available_gpus(self):
        """Get list of available GPU types"""
        available_gpus = []
        for gpu_type, info in self.gpu_info.items():
            if info['available']:
                available_gpus.append({
                    'type': gpu_type,
                    'name': info['name'],
                    'encoders': info['encoders']
                })
        return available_gpus
    
    def get_gpu_encoder(self, gpu_type, video_codec="h264"):
        """Get appropriate encoder for GPU type and video codec"""
        if gpu_type not in self.gpu_info or not self.gpu_info[gpu_type]['available']:
            return None
        
        encoders = self.gpu_info[gpu_type]['encoders']
        
        # Map video codec to encoder
        if video_codec.lower() == "h264":
            for encoder in encoders:
                if "h264" in encoder:
                    return encoder
        elif video_codec.lower() == "hevc":
            for encoder in encoders:
                if "hevc" in encoder:
                    return encoder
        elif video_codec.lower() == "av1":
            for encoder in encoders:
                if "av1" in encoder:
                    return encoder
        
        # Fallback to first available encoder
        return encoders[0] if encoders else None
    
    def get_available_gpu_encoders(self):
        """Get list of available GPU encoders"""
        encoders = []
        for gpu_type, info in self.gpu_info.items():
            if info['available']:
                encoders.extend(info['encoders'])
        return encoders
    
    def get_best_gpu_encoder(self, codec="h264"):
        """Get the best available GPU encoder for a given codec"""
        if codec.lower() == "h264":
            # Priority order: NVIDIA > AMD > Intel > Apple
            for gpu_type in ['nvidia', 'amd', 'intel', 'apple']:
                if self.gpu_info[gpu_type]['available']:
                    if gpu_type == 'nvidia' and 'h264_nvenc' in self.gpu_info[gpu_type]['encoders']:
                        return 'h264_nvenc'
                    elif gpu_type == 'amd' and 'h264_amf' in self.gpu_info[gpu_type]['encoders']:
                        return 'h264_amf'
                    elif gpu_type == 'intel' and 'h264_qsv' in self.gpu_info[gpu_type]['encoders']:
                        return 'h264_qsv'
                    elif gpu_type == 'apple' and 'h264_videotoolbox' in self.gpu_info[gpu_type]['encoders']:
                        return 'h264_videotoolbox'
        
        elif codec.lower() in ["h265", "hevc"]:
            # Priority order: NVIDIA > AMD > Intel > Apple
            for gpu_type in ['nvidia', 'amd', 'intel', 'apple']:
                if self.gpu_info[gpu_type]['available']:
                    if gpu_type == 'nvidia' and 'hevc_nvenc' in self.gpu_info[gpu_type]['encoders']:
                        return 'hevc_nvenc'
                    elif gpu_type == 'amd' and 'hevc_amf' in self.gpu_info[gpu_type]['encoders']:
                        return 'hevc_amf'
                    elif gpu_type == 'intel' and 'hevc_qsv' in self.gpu_info[gpu_type]['encoders']:
                        return 'hevc_qsv'
                    elif gpu_type == 'apple' and 'hevc_videotoolbox' in self.gpu_info[gpu_type]['encoders']:
                        return 'hevc_videotoolbox'
        
        return None
    
    def log_message(self, message, level="INFO"):
        """Log message using callback if available"""
        if self.log_callback:
            self.log_callback(message, level)
    
    def convert_audio_files(self, input_dir, output_dir, input_format, output_format, 
                          quality="standard", audio_codec=None, preserve_metadata=False):
        """Convert audio files using ffmpeg"""
        # Validate input parameters
        if not os.path.exists(input_dir):
            self.log_message(f"Input directory does not exist: {input_dir}", "ERROR")
            return
        
        if input_format == output_format:
            self.log_message("Input and output formats are the same. No conversion needed.", "WARNING")
            return
        
        # Find all audio files of the input format
        pattern = os.path.join(input_dir, f"*.{input_format}")
        audio_files = glob.glob(pattern)
        
        if not audio_files:
            self.log_message(f"No {input_format.upper()} files found in input directory", "WARNING")
            return
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Determine appropriate audio codec based on output format
        if audio_codec is None:
            codec_map = {
                "mp3": "libmp3lame",
                "flac": "flac", 
                "aac": "aac",
                "ogg": "libvorbis",
                "wav": "pcm_s16le",
                "m4a": "aac",
                "wma": "wmav2"
            }
            audio_codec = codec_map.get(output_format.lower(), "aac")
        
        # Get quality settings
        quality_map = {
            "source": None,  # Keep original bitrate
            "high": "320k",
            "standard": "192k", 
            "low": "128k"
        }
        bitrate = quality_map.get(quality, "192k")
        
        # Convert each file
        for audio_file in audio_files:
            filename = os.path.basename(audio_file)
            name, _ = os.path.splitext(filename)
            output_file = os.path.join(output_dir, f"{name}.{output_format}")
            
            self.log_message(f"Converting: {filename}", "INFO")
            
            # Build ffmpeg command
            cmd = [
                "ffmpeg", "-i", audio_file,
                "-c:a", audio_codec,
                "-y",  # Overwrite output files
                output_file
            ]
            
            # Add bitrate only if not source quality and not for lossless formats
            if bitrate is not None and output_format.lower() not in ["flac", "wav"]:
                cmd.insert(-2, "-b:a")
                cmd.insert(-2, bitrate)
            
            # Add metadata preservation if enabled
            if preserve_metadata:
                cmd.extend(["-map_metadata", "0"])
            
            # Run conversion
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log_message(f"Successfully converted: {filename}", "SUCCESS")
            else:
                self.log_message(f"Failed to convert: {filename} - {result.stderr}", "ERROR")

    def convert_single_audio_file(self, input_file, output_dir, output_format,
                                  quality="standard", audio_codec=None, preserve_metadata=False):
        """Convert a single audio file using ffmpeg."""
        if not os.path.exists(input_file):
            self.log_message(f"Input file does not exist: {input_file}", "ERROR")
            return
        os.makedirs(output_dir, exist_ok=True)

        import os as _os
        name, _ = _os.path.splitext(_os.path.basename(input_file))
        output_file = _os.path.join(output_dir, f"{name}.{output_format}")

        # Determine appropriate audio codec based on output format
        if audio_codec is None:
            codec_map = {
                "mp3": "libmp3lame",
                "flac": "flac",
                "aac": "aac",
                "ogg": "libvorbis",
                "wav": "pcm_s16le",
                "m4a": "aac",
                "wma": "wmav2"
            }
            audio_codec = codec_map.get(output_format.lower(), "aac")

        # Get quality settings
        quality_map = {
            "source": None,  # Keep original bitrate
            "high": "320k",
            "standard": "192k", 
            "low": "128k"
        }
        bitrate = quality_map.get(quality, "192k")

        self.log_message(f"Converting: {_os.path.basename(input_file)}", "INFO")

        # Build ffmpeg command
        cmd = [
            "ffmpeg", "-i", input_file,
            "-c:a", audio_codec,
            "-y",  # Overwrite output files
            output_file
        ]

        # Add bitrate only if not source quality and not for lossless formats
        if bitrate is not None and output_format.lower() not in ["flac", "wav"]:
            cmd.insert(-2, "-b:a")
            cmd.insert(-2, bitrate)

        # Add metadata preservation if enabled
        if preserve_metadata:
            cmd.extend(["-map_metadata", "0"])

        # Run conversion
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            self.log_message(f"Successfully converted: {name}", "SUCCESS")
        else:
            self.log_message(f"Failed to convert: {name} - {result.stderr}", "ERROR")
    
    def convert_video_files(self, input_dir, output_dir, input_format, output_format,
                          quality="source", framerate="source", video_codec="h264", 
                          audio_codec="aac", audio_stream_option="first",
                          subtitle_enabled=False, subtitle_format="srt", 
                          subtitle_stream_option="first", preserve_metadata=False,
                          use_gpu=True, force_cpu=False, selected_gpu=None):
        """Convert video files using ffmpeg"""
        # Validate input parameters
        if not os.path.exists(input_dir):
            self.log_message(f"Input directory does not exist: {input_dir}", "ERROR")
            return
        
        if input_format == output_format:
            self.log_message("Input and output formats are the same. No conversion needed.", "WARNING")
            return
        
        # Find all video files of the input format
        pattern = os.path.join(input_dir, f"*.{input_format}")
        video_files = glob.glob(pattern)
        
        if not video_files:
            self.log_message(f"No {input_format.upper()} files found in input directory", "WARNING")
            return
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Override codecs for container-specific requirements
        if output_format.lower() == "webm":
            # WebM supports only VP8/VP9/AV1 video and Vorbis/Opus audio
            self.log_message("WebM requires VP8/VP9/AV1 video and Vorbis/Opus audio. Using VP9 (libvpx-vp9) + Opus.", "INFO")
            video_codec = "libvpx-vp9"
            audio_codec = "libopus"
            use_gpu = False  # GPU encoders generally not supported for VP9 in WebM

        # Determine video encoder (GPU or CPU)
        actual_video_codec = video_codec
        gpu_encoder = None
        
        if use_gpu and not force_cpu:
            if selected_gpu:
                # Use specific GPU if selected
                gpu_encoder = self.get_gpu_encoder(selected_gpu, video_codec)
                if gpu_encoder:
                    actual_video_codec = gpu_encoder
                    gpu_name = self.gpu_info[selected_gpu]['name']
                    self.log_message(f"Using {gpu_name} GPU acceleration: {gpu_encoder}", "INFO")
                else:
                    self.log_message(f"Selected GPU ({selected_gpu}) not available for {video_codec}, using CPU", "WARNING")
            else:
                # Auto-select best GPU
                gpu_encoder = self.get_best_gpu_encoder(video_codec)
                if gpu_encoder:
                    actual_video_codec = gpu_encoder
                    self.log_message(f"Using GPU acceleration: {gpu_encoder}", "INFO")
                else:
                    self.log_message("GPU acceleration not available for this codec, using CPU", "INFO")
        else:
            self.log_message("Using CPU encoding", "INFO")
        
        # Quality settings (different for GPU vs CPU)
        if gpu_encoder:
            # GPU quality settings (using preset and quality)
            quality_map = {
                "source": [],  # Keep original resolution
                "8k": ["-vf", "scale=7680:4320", "-preset", "fast", "-cq", "15"],
                "4k": ["-vf", "scale=3840:2160", "-preset", "fast", "-cq", "18"],
                "high": ["-vf", "scale=1920:1080", "-preset", "fast", "-cq", "18"],
                "standard": ["-vf", "scale=1280:720", "-preset", "fast", "-cq", "23"],
                "low": ["-vf", "scale=854:480", "-preset", "fast", "-cq", "28"]
            }
        else:
            # CPU quality settings (using CRF)
            quality_map = {
                "source": [],  # Keep original resolution
                "8k": ["-vf", "scale=7680:4320", "-crf", "15"],
                "4k": ["-vf", "scale=3840:2160", "-crf", "18"],
                "high": ["-vf", "scale=1920:1080", "-crf", "18"],
                "standard": ["-vf", "scale=1280:720", "-crf", "23"],
                "low": ["-vf", "scale=854:480", "-crf", "28"]
            }
        
        quality_args = quality_map.get(quality, quality_map["source"])
        
        # Framerate settings
        framerate_args = []
        if framerate != "source":
            framerate_args = ["-r", framerate]
        
        # Convert each file
        for video_file in video_files:
            filename = os.path.basename(video_file)
            name, _ = os.path.splitext(filename)
            output_file = os.path.join(output_dir, f"{name}.{output_format}")
            
            self.log_message(f"Converting: {filename}", "INFO")
            
            # Build ffmpeg command
            cmd = [
                "ffmpeg", "-i", video_file,
                "-c:v", actual_video_codec,
                "-c:a", audio_codec
            ] + quality_args + framerate_args + [
                "-y",  # Overwrite output files
                output_file
            ]
            
            # Add metadata preservation if enabled
            if preserve_metadata:
                cmd.extend(["-map_metadata", "0"])
            
            # Handle multiple audio streams
            if audio_stream_option == "all":
                # Extract all audio streams as separate files
                for i in range(10):  # Assume max 10 audio streams
                    audio_output = os.path.join(output_dir, f"{name}_audio_{i}.{output_format}")
                    audio_cmd = ["ffmpeg", "-i", video_file, "-map", f"0:a:{i}", "-c:a", audio_codec, "-y", audio_output]
                    result = subprocess.run(audio_cmd, capture_output=True, text=True)
                    if result.returncode != 0:
                        break  # No more audio streams
            elif audio_stream_option == "best":
                # Use the first audio stream
                cmd.extend(["-map", "0:a:0"])
            elif audio_stream_option == "mix":
                # Mix all audio streams
                cmd.extend(["-filter_complex", "amix=inputs=1", "-map", "0:a"])
            else:  # first
                # Use first audio stream (default)
                cmd.extend(["-map", "0:a:0"])
            
            # Add subtitle support if enabled
            if subtitle_enabled:
                if subtitle_stream_option == "all":
                    # Extract all subtitle streams as separate files
                    for i in range(10):  # Assume max 10 subtitle streams
                        subtitle_output = os.path.join(output_dir, f"{name}_subtitle_{i}.{subtitle_format}")
                        subtitle_cmd = ["ffmpeg", "-i", video_file, "-map", f"0:s:{i}", "-c:s", subtitle_format, "-y", subtitle_output]
                        result = subprocess.run(subtitle_cmd, capture_output=True, text=True)
                        if result.returncode != 0:
                            break  # No more subtitle streams
                elif subtitle_stream_option == "best":
                    # Use the first subtitle stream
                    cmd.extend(["-map", "0:s:0", "-c:s", subtitle_format])
                else:  # first
                    # Use first subtitle stream (default)
                    cmd.extend(["-map", "0:s:0", "-c:s", subtitle_format])
            
            # Run conversion
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.log_message(f"Successfully converted: {filename}", "SUCCESS")
            else:
                self.log_message(f"Failed to convert: {filename} - {result.stderr}", "ERROR")

    def convert_single_video_file(self, input_file, output_dir, output_format,
                                  quality="source", framerate="source", video_codec="h264",
                                  audio_codec="aac", preserve_metadata=False,
                                  use_gpu=True, force_cpu=False, selected_gpu=None):
        """Convert a single video file using ffmpeg."""
        if not os.path.exists(input_file):
            self.log_message(f"Input file does not exist: {input_file}", "ERROR")
            return
        os.makedirs(output_dir, exist_ok=True)

        import os as _os
        name, _ = _os.path.splitext(_os.path.basename(input_file))
        output_file = _os.path.join(output_dir, f"{name}.{output_format}")

        # Override codecs for container-specific requirements
        if output_format.lower() == "webm":
            self.log_message("WebM requires VP8/VP9/AV1 video and Vorbis/Opus audio. Using VP9 (libvpx-vp9) + Opus.", "INFO")
            video_codec = "libvpx-vp9"
            audio_codec = "libopus"
            use_gpu = False

        actual_video_codec = video_codec
        gpu_encoder = None
        if use_gpu and not force_cpu:
            if selected_gpu:
                # Use specific GPU if selected
                gpu_encoder = self.get_gpu_encoder(selected_gpu, video_codec)
                if gpu_encoder:
                    actual_video_codec = gpu_encoder
                    gpu_name = self.gpu_info[selected_gpu]['name']
                    self.log_message(f"Using {gpu_name} GPU acceleration: {gpu_encoder}", "INFO")
                else:
                    self.log_message(f"Selected GPU ({selected_gpu}) not available for {video_codec}, using CPU", "WARNING")
            else:
                # Auto-select best GPU
                gpu_encoder = self.get_best_gpu_encoder(video_codec)
                if gpu_encoder:
                    actual_video_codec = gpu_encoder
                    self.log_message(f"Using GPU acceleration: {gpu_encoder}", "INFO")
                else:
                    self.log_message("GPU acceleration not available for this codec, using CPU", "INFO")
        else:
            self.log_message("Using CPU encoding", "INFO")

        if gpu_encoder:
            quality_map = {
                "source": [],
                "8k": ["-vf", "scale=7680:4320", "-preset", "fast", "-cq", "15"],
                "4k": ["-vf", "scale=3840:2160", "-preset", "fast", "-cq", "18"],
                "high": ["-vf", "scale=1920:1080", "-preset", "fast", "-cq", "18"],
                "standard": ["-vf", "scale=1280:720", "-preset", "fast", "-cq", "23"],
                "low": ["-vf", "scale=854:480", "-preset", "fast", "-cq", "28"]
            }
        else:
            quality_map = {
                "source": [],
                "8k": ["-vf", "scale=7680:4320", "-crf", "15"],
                "4k": ["-vf", "scale=3840:2160", "-crf", "18"],
                "high": ["-vf", "scale=1920:1080", "-crf", "18"],
                "standard": ["-vf", "scale=1280:720", "-crf", "23"],
                "low": ["-vf", "scale=854:480", "-crf", "28"]
            }
        quality_args = quality_map.get(quality, quality_map["source"])
        framerate_args = [] if framerate == "source" else ["-r", framerate]

        cmd = [
            "ffmpeg", "-i", input_file,
            "-c:v", actual_video_codec,
            "-c:a", audio_codec
        ] + quality_args + framerate_args + [
            "-y",
            output_file
        ]
        if preserve_metadata:
            cmd.extend(["-map_metadata", "0"])

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            self.log_message(f"Successfully converted: {name}", "SUCCESS")
        else:
            # If GPU encoding failed, try CPU fallback
            if gpu_encoder and not force_cpu:
                self.log_message(f"GPU encoding failed, falling back to CPU encoding: {result.stderr}", "WARNING")
                
                # Retry with CPU encoding
                cpu_cmd = [
                    "ffmpeg", "-i", input_file,
                    "-c:v", video_codec,  # Use original CPU codec
                    "-c:a", audio_codec
                ] + quality_args + framerate_args + [
                    "-y",
                    output_file
                ]
                if preserve_metadata:
                    cpu_cmd.extend(["-map_metadata", "0"])
                
                cpu_result = subprocess.run(cpu_cmd, capture_output=True, text=True)
                if cpu_result.returncode == 0:
                    self.log_message(f"Successfully converted with CPU fallback: {name}", "SUCCESS")
                else:
                    self.log_message(f"CPU fallback also failed: {name} - {cpu_result.stderr}", "ERROR")
            else:
                self.log_message(f"Failed to convert: {name} - {result.stderr}", "ERROR")
    
    def convert_image_files(self, input_dir, output_dir, input_format, output_format, quality="standard"):
        """Convert image files using PIL"""
        # Validate input parameters
        if not os.path.exists(input_dir):
            self.log_message(f"Input directory does not exist: {input_dir}", "ERROR")
            return
        
        if input_format == output_format:
            self.log_message("Input and output formats are the same. No conversion needed.", "WARNING")
            return
        
        # Find all image files of the input format
        pattern = os.path.join(input_dir, f"*.{input_format}")
        image_files = glob.glob(pattern)
        
        if not image_files:
            self.log_message(f"No {input_format.upper()} files found in input directory", "WARNING")
            return
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Get quality settings
        quality_map = {
            "source": None,  # Keep original quality
            "high": 95,
            "standard": 80,
            "low": 60
        }
        quality_value = quality_map.get(quality, 80)
        
        # Convert each file
        for image_file in image_files:
            filename = os.path.basename(image_file)
            name, _ = os.path.splitext(filename)
            output_file = os.path.join(output_dir, f"{name}.{output_format}")
            
            self.log_message(f"Converting: {filename}", "INFO")
            
            try:
                # Open and convert image
                with Image.open(image_file) as img:
                    # Convert to RGB if necessary (for JPEG output)
                    if output_format.lower() in ['jpg', 'jpeg'] and img.mode in ['RGBA', 'LA', 'P']:
                        img = img.convert('RGB')
                    
                    # Save with quality settings
                    if output_format.lower() in ['jpg', 'jpeg']:
                        if quality_value is not None:
                            img.save(output_file, quality=quality_value, optimize=True)
                        else:
                            # Source quality - save without quality parameter to preserve original
                            img.save(output_file, optimize=True)
                    else:
                        img.save(output_file)
                
                self.log_message(f"Successfully converted: {filename}", "SUCCESS")
                
            except Exception as e:
                self.log_message(f"Failed to convert: {filename} - {str(e)}", "ERROR")

    def convert_single_image_file(self, input_file, output_dir, output_format, quality="standard"):
        """Convert a single image file using PIL."""
        if not os.path.exists(input_file):
            self.log_message(f"Input file does not exist: {input_file}", "ERROR")
            return
        os.makedirs(output_dir, exist_ok=True)

        import os as _os
        name, _ = _os.path.splitext(_os.path.basename(input_file))
        output_file = _os.path.join(output_dir, f"{name}.{output_format}")

        quality_map = {
            "source": None,
            "high": 95,
            "standard": 80,
            "low": 60
        }
        quality_value = quality_map.get(quality, 80)

        try:
            with Image.open(input_file) as img:
                if output_format.lower() in ['jpg', 'jpeg'] and img.mode in ['RGBA', 'LA', 'P']:
                    img = img.convert('RGB')
                if output_format.lower() in ['jpg', 'jpeg']:
                    if quality_value is not None:
                        img.save(output_file, quality=quality_value, optimize=True)
                    else:
                        img.save(output_file, optimize=True)
                else:
                    img.save(output_file)
            self.log_message(f"Successfully converted: {name}", "SUCCESS")
        except Exception as e:
            self.log_message(f"Failed to convert: {name} - {str(e)}", "ERROR")
