"""
Media Converter Page Module
Handles the comprehensive media converter UI and logic
"""

import tkinter as tk
from tkinter import ttk, filedialog
import threading
from src.media_converter import MediaConverter
from src.ui_components import TooltipManager
from src.gui_utils import WindowManager


class MediaConverterPage:
    """Creates the comprehensive Media Converter page"""
    
    def __init__(self, parent, log_callback, dependency_warnings=None):
        self.parent = parent
        self.log_callback = log_callback
        self.dependency_warnings = dependency_warnings or []
        self.converter = MediaConverter(log_callback)
        
        # Initialize variables
        self.media_input_dir_var = tk.StringVar()
        self.media_input_file_var = tk.StringVar()
        self.input_mode_var = tk.StringVar(value="directory")  # directory | single
        self.media_output_dir_var = tk.StringVar()
        self.media_type_var = tk.StringVar(value="audio")
        self.input_format_var = tk.StringVar()
        self.output_format_var = tk.StringVar()
        
        # Quality settings
        self.audio_quality_var = tk.StringVar(value="high")
        self.video_quality_var = tk.StringVar(value="source")
        self.image_quality_var = tk.StringVar(value="high")
        self.framerate_var = tk.StringVar(value="source")
        
        # Advanced options
        self.video_codec_var = tk.StringVar(value="h264")
        self.audio_codec_var = tk.StringVar(value="aac")
        self.subtitle_var = tk.BooleanVar(value=False)
        self.subtitle_format_var = tk.StringVar(value="srt")
        self.subtitle_stream_var = tk.StringVar(value="first")
        self.audio_stream_var = tk.StringVar(value="first")
        self.shared_metadata_var = tk.BooleanVar(value=False)
        
        # GPU acceleration options
        self.use_gpu_var = tk.BooleanVar(value=True)
        self.force_cpu_var = tk.BooleanVar(value=False)
        self.selected_gpu_var = tk.StringVar(value="auto")
        
        # UI mode options
        self.simple_mode_var = tk.BooleanVar(value=True)
        
        # Auto-output directory tracking
        self.output_dir_manually_set = False
        self.media_cancel_event = threading.Event()
        self.job_status_var = tk.StringVar(value="Ready")
    
    def create_page(self):
        """Create the comprehensive Media Converter page"""
        page = ttk.Frame(self.parent, style='Content.TFrame')
        
        # Page title
        title_label = ttk.Label(page, text="Media Converter", style='Title.TLabel')
        title_label.pack(anchor=tk.W, pady=(0, 16))

        if self.dependency_warnings:
            banner = tk.Frame(page, bg='#332A12', highlightthickness=1, highlightbackground='#7A5B00')
            banner.pack(fill=tk.X, pady=(0, 14))
            banner_text = tk.Label(
                banner,
                text=self.dependency_warnings[0],
                font=('Segoe UI', 9),
                bg='#332A12',
                fg='#FFDF7E',
                anchor='w',
                wraplength=720,
                justify=tk.LEFT,
                padx=12,
                pady=8,
            )
            banner_text.pack(fill=tk.X)
        
        # Simple Mode toggle
        mode_frame = ttk.Frame(page)
        mode_frame.pack(fill=tk.X, pady=(0, 20))
        
        simple_mode_checkbox = ttk.Checkbutton(
            mode_frame, 
            text="Simple Mode (format conversion only)",
            variable=self.simple_mode_var,
            command=self.toggle_simple_mode
        )
        simple_mode_checkbox.pack(side=tk.LEFT)
        TooltipManager.create_tooltip(simple_mode_checkbox, "Hide advanced options and use optimal settings for format-only conversion")
        
        # Simple mode status label
        self.simple_mode_status = ttk.Label(
            mode_frame, 
            text="Optimized settings",
            style='Success.TLabel'
        )
        self.simple_mode_status.pack(side=tk.LEFT, padx=(20, 0))
        
        # Create scrollable content with Windows 11 dark theme background
        canvas = tk.Canvas(page, bg='#202020', highlightthickness=0, borderwidth=0)
        scrollbar = ttk.Scrollbar(page, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Content.TFrame')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(canvas_window, width=e.width))
        
        # Enable mouse wheel scrolling on the main content (Windows/Mac/Linux)
        def _on_mousewheel(event):
            try:
                # Windows / MacOS: event.delta is a multiple of 120 on Windows
                if hasattr(event, "delta") and event.delta:
                    canvas.yview_scroll(int(-event.delta / 120), "units")
                # Linux: Button-4 (up) / Button-5 (down)
                elif getattr(event, "num", None) in (4, 5):
                    canvas.yview_scroll(-1 if event.num == 4 else 1, "units")
            except Exception:
                pass

        # Bind mouse wheel to both the canvas and the inner frame
        canvas.bind("<MouseWheel>", _on_mousewheel)
        canvas.bind("<Button-4>", _on_mousewheel)
        canvas.bind("<Button-5>", _on_mousewheel)
        scrollable_frame.bind("<MouseWheel>", _on_mousewheel)
        scrollable_frame.bind("<Button-4>", _on_mousewheel)
        scrollable_frame.bind("<Button-5>", _on_mousewheel)
        
        # Input/Output Selection Card - Modern Windows 11 style
        io_card, io_content = WindowManager.create_modern_section(scrollable_frame, "Input and Output")
        io_card.pack(fill=tk.X, pady=(0, 24), padx=0)
        
        # Mode toggle (Directory vs Single File)
        mode_frame = ttk.Frame(io_content)
        mode_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Radiobutton(mode_frame, text="Directory Mode", variable=self.input_mode_var, value="directory", command=self.update_source_visibility).pack(side=tk.LEFT, padx=(0, 15))
        ttk.Radiobutton(mode_frame, text="Single File Mode", variable=self.input_mode_var, value="single", command=self.update_source_visibility).pack(side=tk.LEFT)

        # Input directory
        self.input_dir_label = ttk.Label(io_content, text="Input Directory:", style='Info.TLabel')
        input_frame = ttk.Frame(io_content)
        
        input_entry = ttk.Entry(input_frame, textvariable=self.media_input_dir_var, width=60, font=('Segoe UI', 10))
        input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 15))
        
        input_browse_btn = WindowManager.create_gray_button(input_frame, text="Browse", command=self.browse_media_input_directory)
        input_browse_btn.pack(side=tk.RIGHT)

        # Input file (shown in single mode)
        self.input_file_label = ttk.Label(io_content, text="Input File:", style='Info.TLabel')
        self.input_file_frame = ttk.Frame(io_content)
        self.input_file_entry = ttk.Entry(self.input_file_frame, textvariable=self.media_input_file_var, width=60, font=('Segoe UI', 10))
        self.input_file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 15))
        self.input_file_btn = WindowManager.create_gray_button(self.input_file_frame, text="Browse File", command=self.browse_media_input_file)
        self.input_file_btn.pack(side=tk.RIGHT)
        
        # Output directory
        output_frame = ttk.Frame(io_content)
        output_frame.pack(fill=tk.X, pady=(0, 0))
        
        ttk.Label(output_frame, text="Output Directory:", style='Info.TLabel').pack(anchor=tk.W)
        output_entry = ttk.Entry(output_frame, textvariable=self.media_output_dir_var, width=60, font=('Segoe UI', 10))
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 15))
        
        output_browse_btn = WindowManager.create_gray_button(output_frame, text="Browse", command=self.browse_media_output_directory)
        output_browse_btn.pack(side=tk.RIGHT)

        # Initial visibility - set up widget references
        self._dir_widgets = [self.input_dir_label, input_frame]
        self._file_widgets = [self.input_file_label, self.input_file_frame]
        
        # Initially hide file widgets since directory mode is default
        self._file_widgets[0].pack_forget()
        self._file_widgets[1].pack_forget()
        
        # Defer simple mode activation until all sections are created
        
        # Media Type Selection Card - Modern Windows 11 style
        type_card, type_content = WindowManager.create_modern_section(scrollable_frame, "Media Type")
        type_card.pack(fill=tk.X, pady=(0, 24), padx=0)
        
        self.media_type_segment = WindowManager.create_segmented_control(
            type_content,
            self.media_type_var,
            [
                ("Audio", "audio"),
                ("Image", "image"),
                ("Video", "video"),
            ],
            command=self.update_format_options,
        )
        self.media_type_segment.pack(anchor=tk.W)
        
        # Format Selection Card - Modern Windows 11 style
        self.format_card, format_content = WindowManager.create_modern_section(scrollable_frame, "Format")
        self.format_card.pack(fill=tk.X, pady=(0, 24), padx=0)
        
        format_row = ttk.Frame(format_content)
        format_row.pack(fill=tk.X)

        from_format_frame = ttk.Frame(format_row)
        from_format_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(from_format_frame, text="From:", style='Info.TLabel').pack(anchor=tk.W, pady=(0, 5))
        self.input_format_combo = ttk.Combobox(from_format_frame, textvariable=self.input_format_var, state="readonly", font=('Segoe UI', 10))
        self.input_format_combo.pack(fill=tk.X, pady=(0, 0))
        self.input_format_combo.bind('<<ComboboxSelected>>', self.on_input_format_change)

        ttk.Label(format_row, text="->", style='Info.TLabel').pack(side=tk.LEFT, padx=14, pady=(20, 0))
        
        # Output format
        output_format_frame = ttk.Frame(format_row)
        output_format_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(output_format_frame, text="To:", style='Info.TLabel').pack(anchor=tk.W, pady=(0, 5))
        self.output_format_combo = ttk.Combobox(output_format_frame, textvariable=self.output_format_var, state="readonly", font=('Segoe UI', 10))
        self.output_format_combo.pack(fill=tk.X, pady=(0, 0))
        
        # Quality and advanced settings are collapsible to keep the main path compact.
        self.quality_card, quality_content = WindowManager.create_collapsible_section(scrollable_frame, "Quality", expanded=True)
        self.quality_card.pack(fill=tk.X, pady=(0, 24), padx=0)
        
        # Audio quality settings
        self.audio_quality_frame = ttk.Frame(quality_content)
        self.audio_quality_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(self.audio_quality_frame, text="Audio Quality:", style='Info.TLabel').pack(anchor=tk.W, pady=(0, 5))
        ttk.Radiobutton(self.audio_quality_frame, text="Source Quality (keep original)", variable=self.audio_quality_var, value="source").pack(anchor=tk.W, pady=(0, 5))
        ttk.Radiobutton(self.audio_quality_frame, text="High Quality (320 kbps)", variable=self.audio_quality_var, value="high").pack(anchor=tk.W, pady=(0, 5))
        ttk.Radiobutton(self.audio_quality_frame, text="Standard Quality (192 kbps)", variable=self.audio_quality_var, value="standard").pack(anchor=tk.W, pady=(0, 5))
        ttk.Radiobutton(self.audio_quality_frame, text="Low Quality (128 kbps)", variable=self.audio_quality_var, value="low").pack(anchor=tk.W, pady=(0, 0))
        
        # Video quality settings
        self.video_quality_frame = ttk.Frame(quality_content)
        self.video_quality_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(self.video_quality_frame, text="Video Resolution:", style='Info.TLabel').pack(anchor=tk.W, pady=(0, 5))
        ttk.Radiobutton(self.video_quality_frame, text="Source Resolution (keep original)", variable=self.video_quality_var, value="source").pack(anchor=tk.W, pady=(0, 5))
        ttk.Radiobutton(self.video_quality_frame, text="8K Ultra (7680x4320)", variable=self.video_quality_var, value="8k").pack(anchor=tk.W, pady=(0, 5))
        ttk.Radiobutton(self.video_quality_frame, text="4K Ultra (3840x2160)", variable=self.video_quality_var, value="4k").pack(anchor=tk.W, pady=(0, 5))
        ttk.Radiobutton(self.video_quality_frame, text="High Quality (1080p)", variable=self.video_quality_var, value="high").pack(anchor=tk.W, pady=(0, 5))
        ttk.Radiobutton(self.video_quality_frame, text="Standard Quality (720p)", variable=self.video_quality_var, value="standard").pack(anchor=tk.W, pady=(0, 5))
        ttk.Radiobutton(self.video_quality_frame, text="Low Quality (480p)", variable=self.video_quality_var, value="low").pack(anchor=tk.W, pady=(0, 15))
        
        # Framerate settings
        ttk.Label(self.video_quality_frame, text="Framerate:", style='Info.TLabel').pack(anchor=tk.W, pady=(0, 5))
        ttk.Radiobutton(self.video_quality_frame, text="Source Framerate (keep original)", variable=self.framerate_var, value="source").pack(anchor=tk.W, pady=(0, 5))
        ttk.Radiobutton(self.video_quality_frame, text="60 FPS (smooth)", variable=self.framerate_var, value="60").pack(anchor=tk.W, pady=(0, 5))
        ttk.Radiobutton(self.video_quality_frame, text="30 FPS (standard)", variable=self.framerate_var, value="30").pack(anchor=tk.W, pady=(0, 5))
        ttk.Radiobutton(self.video_quality_frame, text="24 FPS (cinematic)", variable=self.framerate_var, value="24").pack(anchor=tk.W, pady=(0, 0))
        
        # Image quality settings
        self.image_quality_frame = ttk.Frame(quality_content)
        self.image_quality_frame.pack(fill=tk.X, pady=(0, 0))
        
        ttk.Label(self.image_quality_frame, text="Image Quality:", style='Info.TLabel').pack(anchor=tk.W, pady=(0, 5))
        ttk.Radiobutton(self.image_quality_frame, text="Source Quality (keep original)", variable=self.image_quality_var, value="source").pack(anchor=tk.W, pady=(0, 5))
        ttk.Radiobutton(self.image_quality_frame, text="High Quality (95%)", variable=self.image_quality_var, value="high").pack(anchor=tk.W, pady=(0, 5))
        ttk.Radiobutton(self.image_quality_frame, text="Standard Quality (80%)", variable=self.image_quality_var, value="standard").pack(anchor=tk.W, pady=(0, 5))
        ttk.Radiobutton(self.image_quality_frame, text="Low Quality (60%)", variable=self.image_quality_var, value="low").pack(anchor=tk.W, pady=(0, 0))
        
        self.encoding_card, encoding_content = WindowManager.create_collapsible_section(scrollable_frame, "Encoding", expanded=True)
        self.encoding_card.pack(fill=tk.X, pady=(0, 24), padx=0)
        
        # Video encoding options
        self.video_encoding_frame = ttk.Frame(encoding_content)
        self.video_encoding_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(self.video_encoding_frame, text="Video Codec:", style='Info.TLabel').pack(anchor=tk.W, pady=(0, 5))
        ttk.Radiobutton(self.video_encoding_frame, text="H.264 (compatible)", variable=self.video_codec_var, value="h264").pack(anchor=tk.W, pady=(0, 5))
        ttk.Radiobutton(self.video_encoding_frame, text="H.265 (efficient)", variable=self.video_codec_var, value="h265").pack(anchor=tk.W, pady=(0, 5))
        ttk.Radiobutton(self.video_encoding_frame, text="VP9 (web optimized)", variable=self.video_codec_var, value="vp9").pack(anchor=tk.W, pady=(0, 0))
        
        # Audio encoding options
        self.audio_encoding_frame = ttk.Frame(encoding_content)
        self.audio_encoding_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(self.audio_encoding_frame, text="Audio Codec:", style='Info.TLabel').pack(anchor=tk.W, pady=(0, 5))
        ttk.Radiobutton(self.audio_encoding_frame, text="AAC (compatible)", variable=self.audio_codec_var, value="aac").pack(anchor=tk.W, pady=(0, 5))
        ttk.Radiobutton(self.audio_encoding_frame, text="MP3 (universal)", variable=self.audio_codec_var, value="mp3").pack(anchor=tk.W, pady=(0, 5))
        ttk.Radiobutton(self.audio_encoding_frame, text="Opus (efficient)", variable=self.audio_codec_var, value="opus").pack(anchor=tk.W, pady=(0, 0))

        self.streams_card, streams_content = WindowManager.create_collapsible_section(scrollable_frame, "Streams", expanded=False)
        self.streams_card.pack(fill=tk.X, pady=(0, 24), padx=0)
        
        # Multiple audio stream handling
        self.audio_stream_frame = ttk.Frame(streams_content)
        self.audio_stream_frame.pack(fill=tk.X)
        ttk.Label(self.audio_stream_frame, text="Multiple Audio Streams:", style='Info.TLabel').pack(anchor=tk.W, pady=(0, 5))
        ttk.Radiobutton(self.audio_stream_frame, text="Use first stream only", variable=self.audio_stream_var, value="first").pack(anchor=tk.W, pady=(0, 5))
        ttk.Radiobutton(self.audio_stream_frame, text="Use all streams (separate files)", variable=self.audio_stream_var, value="all").pack(anchor=tk.W, pady=(0, 5))
        ttk.Radiobutton(self.audio_stream_frame, text="Use best quality stream", variable=self.audio_stream_var, value="best").pack(anchor=tk.W, pady=(0, 5))
        ttk.Radiobutton(self.audio_stream_frame, text="Mix all streams", variable=self.audio_stream_var, value="mix").pack(anchor=tk.W, pady=(0, 0))

        self.subtitle_card, subtitle_content = WindowManager.create_collapsible_section(scrollable_frame, "Subtitles", expanded=False)
        self.subtitle_card.pack(fill=tk.X, pady=(0, 24), padx=0)
        
        # Subtitle options
        self.subtitle_frame = ttk.Frame(subtitle_content)
        self.subtitle_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.subtitle_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(self.subtitle_frame, text="Include subtitles", variable=self.subtitle_var).pack(anchor=tk.W, pady=(0, 5))
        
        # Subtitle format selection with tooltips
        subtitle_format_frame = ttk.Frame(self.subtitle_frame)
        subtitle_format_frame.pack(fill=tk.X, pady=(0, 5))
        
        srt_radio = ttk.Radiobutton(subtitle_format_frame, text="SRT Format", variable=self.subtitle_format_var, value="srt")
        srt_radio.pack(anchor=tk.W, pady=(0, 5))
        TooltipManager.create_tooltip(srt_radio, "SRT: Simple text-based format with timestamps. Compatible with most players and editing software.")
        
        vtt_radio = ttk.Radiobutton(subtitle_format_frame, text="VTT Format", variable=self.subtitle_format_var, value="vtt")
        vtt_radio.pack(anchor=tk.W, pady=(0, 5))
        TooltipManager.create_tooltip(vtt_radio, "VTT: WebVTT format with HTML-like styling. Better for web players and modern applications.")
        
        # Multiple subtitle stream handling
        ttk.Label(self.subtitle_frame, text="Multiple Subtitle Streams:", style='Info.TLabel').pack(anchor=tk.W, pady=(10, 5))
        ttk.Radiobutton(self.subtitle_frame, text="Use first stream only", variable=self.subtitle_stream_var, value="first").pack(anchor=tk.W, pady=(0, 5))
        ttk.Radiobutton(self.subtitle_frame, text="Use all streams (separate files)", variable=self.subtitle_stream_var, value="all").pack(anchor=tk.W, pady=(0, 5))
        ttk.Radiobutton(self.subtitle_frame, text="Use best quality stream", variable=self.subtitle_stream_var, value="best").pack(anchor=tk.W, pady=(0, 0))

        self.metadata_gpu_card, metadata_gpu_content = WindowManager.create_collapsible_section(scrollable_frame, "Metadata and GPU", expanded=True)
        self.metadata_gpu_card.pack(fill=tk.X, pady=(0, 24), padx=0)
        
        # Shared metadata option
        self.metadata_frame = ttk.Frame(metadata_gpu_content)
        self.metadata_frame.pack(fill=tk.X, pady=(0, 0))
        
        ttk.Checkbutton(self.metadata_frame, text="Share metadata between audio and video", variable=self.shared_metadata_var).pack(anchor=tk.W, pady=(0, 15))
        
        # GPU acceleration settings
        self.gpu_frame = ttk.Frame(metadata_gpu_content)
        self.gpu_frame.pack(fill=tk.X, pady=(0, 0))
        
        ttk.Label(self.gpu_frame, text="GPU Acceleration:", style='Info.TLabel').pack(anchor=tk.W, pady=(0, 5))
        
        # GPU status display
        gpu_status = self.get_gpu_status_text()
        self.gpu_status_label = ttk.Label(self.gpu_frame, text=gpu_status, style='Info.TLabel', font=('Segoe UI', 9))
        self.gpu_status_label.pack(anchor=tk.W, pady=(0, 10))
        
        # GPU options
        gpu_checkbox = ttk.Checkbutton(self.gpu_frame, text="Use GPU acceleration (if available)", variable=self.use_gpu_var, command=self.update_gpu_selection_visibility)
        gpu_checkbox.pack(anchor=tk.W, pady=(0, 5))
        TooltipManager.create_tooltip(gpu_checkbox, "Enable GPU acceleration for faster video encoding. Automatically detects and uses NVIDIA, AMD, Intel, or Apple GPU encoders.")
        
        # GPU selection dropdown
        gpu_selection_frame = ttk.Frame(self.gpu_frame)
        gpu_selection_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(gpu_selection_frame, text="GPU Selection:", style='Info.TLabel').pack(side=tk.LEFT, padx=(0, 10))
        self.gpu_combo = ttk.Combobox(gpu_selection_frame, textvariable=self.selected_gpu_var, state="readonly", width=20)
        self.gpu_combo.pack(side=tk.LEFT)
        self.update_gpu_selection_options()
        
        cpu_checkbox = ttk.Checkbutton(self.gpu_frame, text="Force CPU encoding", variable=self.force_cpu_var, command=self.update_gpu_selection_visibility)
        cpu_checkbox.pack(anchor=tk.W, pady=(0, 0))
        TooltipManager.create_tooltip(cpu_checkbox, "Force CPU encoding even if GPU is available. Useful for maximum quality or compatibility.")
        
        footer = tk.Frame(page, bg='#252525', highlightthickness=1, highlightbackground='#3D3D3D')
        footer.pack(side=tk.BOTTOM, fill=tk.X, pady=(12, 0))
        status_label = tk.Label(
            footer,
            textvariable=self.job_status_var,
            font=('Segoe UI', 10),
            bg='#252525',
            fg='#C0C0C0',
            anchor='w',
        )
        status_label.pack(side=tk.LEFT, padx=14, pady=10, fill=tk.X, expand=True)
        self.media_convert_start_btn = WindowManager.create_gray_button(footer, text="Start Conversion", command=self.start_media_conversion)
        self.media_convert_start_btn.pack(side=tk.RIGHT, padx=(8, 14), pady=8)
        
        self.media_convert_stop_btn = WindowManager.create_gray_button(footer, text="Stop", command=self.stop_media_conversion, state=tk.DISABLED)
        self.media_convert_stop_btn.pack(side=tk.RIGHT, pady=8)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel to canvas
        WindowManager.bind_mousewheel(canvas, scrollbar)
        
        # Initialize format options and visibility
        self.update_format_options()
        
        # Initially hide all advanced options until media type is selected
        self.video_encoding_frame.pack_forget()
        self.audio_encoding_frame.pack_forget()
        self.subtitle_frame.pack_forget()
        self.metadata_frame.pack_forget()
        
        # Initially hide all quality options until media type is selected
        self.audio_quality_frame.pack_forget()
        self.video_quality_frame.pack_forget()
        self.image_quality_frame.pack_forget()
        
        # Finally, activate simple mode default after all widgets exist
        self.toggle_simple_mode()

        return page
    
    def get_gpu_status_text(self):
        """Get GPU status text for display"""
        gpu_info = self.converter.gpu_info
        available_gpus = []
        
        if gpu_info['nvidia']['available']:
            available_gpus.append("NVIDIA")
        if gpu_info['amd']['available']:
            available_gpus.append("AMD")
        if gpu_info['intel']['available']:
            available_gpus.append("Intel")
        if gpu_info['apple']['available']:
            available_gpus.append("Apple")
        
        if available_gpus:
            return f"GPU acceleration available: {', '.join(available_gpus)}"
        else:
            return "No GPU acceleration detected - using CPU encoding"
    
    def update_gpu_selection_options(self):
        """Update GPU selection dropdown options"""
        available_gpus = self.converter.get_available_gpus()
        
        options = ["auto (Auto-select best GPU)"]
        for gpu in available_gpus:
            options.append(f"{gpu['type']} ({gpu['name']})")
        
        self.gpu_combo['values'] = options
        if not self.selected_gpu_var.get() or self.selected_gpu_var.get() not in options:
            self.selected_gpu_var.set(options[0])
    
    def update_gpu_selection_visibility(self):
        """Update GPU selection visibility based on settings"""
        gpu_enabled = self.use_gpu_var.get() and not self.force_cpu_var.get()
        
        # Enable/disable GPU selection based on GPU acceleration setting
        if hasattr(self, 'gpu_combo'):
            if gpu_enabled:
                self.gpu_combo.configure(state="readonly")
            else:
                self.gpu_combo.configure(state="disabled")
    
    def toggle_simple_mode(self):
        """Toggle between simple and advanced mode"""
        is_simple = self.simple_mode_var.get()
        
        if is_simple:
            # Hide advanced sections
            self.quality_card.pack_forget()
            self.encoding_card.pack_forget()
            self.streams_card.pack_forget()
            self.subtitle_card.pack_forget()
            self.metadata_gpu_card.pack_forget()
            
            # Show simple mode status
            self.simple_mode_status.pack(side=tk.LEFT, padx=(20, 0))
            
            # Set optimal defaults for format-only conversion
            self.audio_quality_var.set("source")
            self.video_quality_var.set("source") 
            self.image_quality_var.set("high")
            self.framerate_var.set("source")
            self.video_codec_var.set("h264")
            self.audio_codec_var.set("aac")
            self.subtitle_var.set(False)
            self.shared_metadata_var.set(True)  # Preserve metadata
            self.use_gpu_var.set(True)  # Use GPU for speed
            self.force_cpu_var.set(False)
            self.selected_gpu_var.set("auto (Auto-select best GPU)")
        else:
            # Hide simple mode status
            self.simple_mode_status.pack_forget()
            
            # Show advanced sections for the current media type.
            self.update_quality_visibility()
    
    def browse_media_input_directory(self):
        """Browse for media input directory"""
        directory = filedialog.askdirectory(title="Select Input Directory")
        if directory:
            self.media_input_dir_var.set(directory)
            # Auto-set output directory unless manually set
            if not self.output_dir_manually_set:
                self.media_output_dir_var.set(directory)
    
    def browse_media_input_file(self):
        """Browse for a single input file based on media type"""
        media_type = self.media_type_var.get()
        patterns = {
            "audio": [("Audio", "*.wav;*.flac;*.mp3;*.aac;*.ogg;*.m4a;*.wma")],
            "image": [("Images", "*.jpg;*.jpeg;*.png;*.bmp;*.tiff;*.gif;*.webp")],
            "video": [("Videos", "*.mp4;*.avi;*.mkv;*.mov;*.wmv;*.flv;*.webm")],
        }
        file_path = filedialog.askopenfilename(title="Select Input File", filetypes=patterns.get(media_type, [("All", "*.*")]))
        if file_path:
            self.media_input_file_var.set(file_path)
            # Auto-set output directory to parent dir unless manually set
            import os
            if not self.output_dir_manually_set:
                self.media_output_dir_var.set(os.path.dirname(file_path))
    
    def browse_media_output_directory(self):
        """Browse for media output directory"""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.media_output_dir_var.set(directory)
            self.output_dir_manually_set = True
    
    def update_format_options(self):
        """Update format options based on selected media type"""
        media_type = self.media_type_var.get()
        if hasattr(self, 'media_type_segment'):
            self.media_type_segment.refresh()
        
        # Define format options for each media type
        format_options = {
            "audio": {
                "input": ["WAV", "FLAC", "MP3", "AAC", "OGG", "M4A", "WMA"],
                "output": ["MP3", "AAC", "FLAC", "OGG", "WAV", "M4A", "WMA"]
            },
            "image": {
                "input": ["JPEG", "PNG", "BMP", "TIFF", "GIF", "WebP", "RAW"],
                "output": ["JPEG", "PNG", "BMP", "TIFF", "WebP", "GIF"]
            },
            "video": {
                "input": ["MP4", "AVI", "MKV", "MOV", "WMV", "FLV", "WebM"],
                "output": ["MP4", "AVI", "MKV", "MOV", "WebM", "FLV"]
            }
        }
        
        # Update combobox options
        if media_type in format_options:
            self.input_format_combo['values'] = format_options[media_type]["input"]
            self.output_format_combo['values'] = format_options[media_type]["output"]
            
            # Set default values
            if format_options[media_type]["input"]:
                self.input_format_var.set(format_options[media_type]["input"][0])
            if format_options[media_type]["output"]:
                self.output_format_var.set(format_options[media_type]["output"][0])
        
        # Update visibility of quality settings
        self.update_quality_visibility()
        self.update_source_visibility()

    def update_source_visibility(self):
        """Toggle between directory and single file inputs"""
        is_directory = self.input_mode_var.get() == "directory"
        
        # Show/hide directory widgets
        if is_directory:
            # Show directory widgets
            self._dir_widgets[0].pack(anchor=tk.W, pady=(0, 10))  # label
            self._dir_widgets[1].pack(fill=tk.X, pady=(0, 15))  # frame
            
            # Hide file widgets
            self._file_widgets[0].pack_forget()  # label
            self._file_widgets[1].pack_forget()  # frame
        else:
            # Hide directory widgets
            self._dir_widgets[0].pack_forget()  # label
            self._dir_widgets[1].pack_forget()  # frame
            
            # Show file widgets
            self._file_widgets[0].pack(anchor=tk.W, pady=(0, 10))  # label
            self._file_widgets[1].pack(fill=tk.X, pady=(0, 15))  # frame
    
    def on_input_format_change(self, event=None):
        """Handle input format change to prevent same input/output format"""
        input_format = self.input_format_var.get()
        media_type = self.media_type_var.get()
        
        # Get available output formats
        format_options = {
            "audio": ["MP3", "AAC", "FLAC", "OGG", "WAV", "M4A", "WMA"],
            "image": ["JPEG", "PNG", "BMP", "TIFF", "WebP", "GIF"],
            "video": ["MP4", "AVI", "MKV", "MOV", "WebM", "FLV"]
        }
        
        if media_type in format_options:
            # Filter out the input format from output options
            available_outputs = [fmt for fmt in format_options[media_type] if fmt != input_format]
            self.output_format_combo['values'] = available_outputs
            
            # If current output format is the same as input, change it
            if self.output_format_var.get() == input_format and available_outputs:
                self.output_format_var.set(available_outputs[0])
    
    def update_quality_visibility(self):
        """Update visibility of quality settings based on media type"""
        media_type = self.media_type_var.get()

        if self.simple_mode_var.get():
            self.quality_card.pack_forget()
            self.encoding_card.pack_forget()
            self.streams_card.pack_forget()
            self.subtitle_card.pack_forget()
            self.metadata_gpu_card.pack_forget()
            return

        self.quality_card.pack(fill=tk.X, pady=(0, 24), padx=0)
        
        # Show/hide quality frames based on media type
        if media_type == "audio":
            self.audio_quality_frame.pack(fill=tk.X, pady=(0, 15))
            self.video_quality_frame.pack_forget()
            self.image_quality_frame.pack_forget()
        elif media_type == "video":
            self.audio_quality_frame.pack_forget()
            self.video_quality_frame.pack(fill=tk.X, pady=(0, 15))
            self.image_quality_frame.pack_forget()
        elif media_type == "image":
            self.audio_quality_frame.pack_forget()
            self.video_quality_frame.pack_forget()
            self.image_quality_frame.pack(fill=tk.X, pady=(0, 0))
        
        # Update advanced options visibility
        self.update_advanced_visibility()
    
    def update_advanced_visibility(self):
        """Update visibility of advanced options based on media type"""
        media_type = self.media_type_var.get()

        for card in (self.encoding_card, self.streams_card, self.subtitle_card, self.metadata_gpu_card):
            card.pack_forget()
        
        if media_type == "audio":
            # Show only audio encoding options
            self.encoding_card.pack(fill=tk.X, pady=(0, 24), padx=0)
            self.metadata_gpu_card.pack(fill=tk.X, pady=(0, 24), padx=0)
            self.audio_encoding_frame.pack(fill=tk.X, pady=(0, 15))
            self.video_encoding_frame.pack_forget()
            self.audio_stream_frame.pack_forget()
            self.subtitle_frame.pack_forget()
            self.metadata_frame.pack(fill=tk.X, pady=(0, 0))
            self.gpu_frame.pack_forget()
            
        elif media_type == "video":
            # Show video encoding, audio encoding, subtitles, and metadata options
            self.encoding_card.pack(fill=tk.X, pady=(0, 24), padx=0)
            self.streams_card.pack(fill=tk.X, pady=(0, 24), padx=0)
            self.subtitle_card.pack(fill=tk.X, pady=(0, 24), padx=0)
            self.metadata_gpu_card.pack(fill=tk.X, pady=(0, 24), padx=0)
            self.video_encoding_frame.pack(fill=tk.X, pady=(0, 15))
            self.audio_encoding_frame.pack(fill=tk.X, pady=(0, 15))
            self.audio_stream_frame.pack(fill=tk.X)
            self.subtitle_frame.pack(fill=tk.X, pady=(0, 15))
            self.metadata_frame.pack(fill=tk.X, pady=(0, 0))
            self.gpu_frame.pack(fill=tk.X, pady=(0, 0))
            
        elif media_type == "image":
            # Hide all advanced options for images (they don't need encoding/subtitle options)
            self.video_encoding_frame.pack_forget()
            self.audio_encoding_frame.pack_forget()
            self.audio_stream_frame.pack_forget()
            self.subtitle_frame.pack_forget()
            self.metadata_frame.pack_forget()
            self.gpu_frame.pack_forget()
    
    def start_media_conversion(self):
        """Start media conversion process"""
        mode = self.input_mode_var.get()
        
        # Validate inputs based on mode
        if mode == "directory":
            if not self.media_input_dir_var.get():
                self.log_callback("Please select an input directory", "ERROR")
                return
        else:  # single file mode
            if not self.media_input_file_var.get():
                self.log_callback("Please select an input file", "ERROR")
                return
        
        if not self.media_output_dir_var.get():
            self.log_callback("Please select an output directory", "ERROR")
            return
        
        input_format = self.input_format_var.get()
        output_format = self.output_format_var.get()
        
        if input_format == output_format:
            self.log_callback("Input and output formats cannot be the same", "ERROR")
            return
        
        # Update button states
        self.media_convert_start_btn.configure(state=tk.DISABLED)
        self.media_convert_stop_btn.configure(state=tk.NORMAL)
        self.job_status_var.set("Running conversion...")
        self.media_cancel_event = threading.Event()
        
        # Start conversion in a separate thread
        self.media_conversion_thread = threading.Thread(target=self.run_media_conversion)
        self.media_conversion_thread.daemon = True
        self.media_conversion_thread.start()
    
    def run_media_conversion(self):
        """Run the media conversion process"""
        try:
            media_type = self.media_type_var.get()
            input_dir = self.media_input_dir_var.get()
            input_file = self.media_input_file_var.get()
            mode = self.input_mode_var.get()
            output_dir = self.media_output_dir_var.get()
            input_format = self.input_format_var.get().lower()
            output_format = self.output_format_var.get().lower()
            
            self.log_callback(f"Starting {media_type} conversion from {input_format} to {output_format}", "INFO")
            
            # Build conversion parameters
            summary = None

            if media_type == "audio":
                if mode == "single":
                    from os.path import dirname
                    if not output_dir:
                        output_dir = dirname(input_file)
                    # For single file conversion, let the converter determine the appropriate codec
                    # based on the output format rather than using the GUI codec selection
                    summary = self.converter.convert_single_audio_file(
                        input_file, output_dir, output_format,
                        quality=self.audio_quality_var.get(),
                        audio_codec=None,  # Let the method determine the correct codec
                        preserve_metadata=self.shared_metadata_var.get(),
                        cancel_event=self.media_cancel_event
                    )
                else:
                    summary = self.converter.convert_audio_files(
                        input_dir, output_dir, input_format, output_format,
                        quality=self.audio_quality_var.get(),
                        audio_codec=self.audio_codec_var.get(),
                        preserve_metadata=self.shared_metadata_var.get(),
                        cancel_event=self.media_cancel_event
                    )
            elif media_type == "video":
                if mode == "single":
                    from os.path import dirname
                    if not output_dir:
                        output_dir = dirname(input_file)
                    # Get selected GPU
                    selected_gpu = None
                    if self.use_gpu_var.get() and not self.force_cpu_var.get():
                        gpu_selection = self.selected_gpu_var.get()
                        if gpu_selection and gpu_selection != "auto (Auto-select best GPU)":
                            selected_gpu = gpu_selection.split(" ")[0]  # Extract GPU type
                    
                    summary = self.converter.convert_single_video_file(
                        input_file, output_dir, output_format,
                        quality=self.video_quality_var.get(),
                        framerate=self.framerate_var.get(),
                        video_codec=self.video_codec_var.get(),
                        audio_codec=self.audio_codec_var.get(),
                        preserve_metadata=self.shared_metadata_var.get(),
                        use_gpu=self.use_gpu_var.get(),
                        force_cpu=self.force_cpu_var.get(),
                        selected_gpu=selected_gpu,
                        cancel_event=self.media_cancel_event
                    )
                else:
                    # Get selected GPU
                    selected_gpu = None
                    if self.use_gpu_var.get() and not self.force_cpu_var.get():
                        gpu_selection = self.selected_gpu_var.get()
                        if gpu_selection and gpu_selection != "auto (Auto-select best GPU)":
                            selected_gpu = gpu_selection.split(" ")[0]  # Extract GPU type
                    
                    summary = self.converter.convert_video_files(
                        input_dir, output_dir, input_format, output_format,
                        quality=self.video_quality_var.get(),
                        framerate=self.framerate_var.get(),
                        video_codec=self.video_codec_var.get(),
                        audio_codec=self.audio_codec_var.get(),
                        audio_stream_option=self.audio_stream_var.get(),
                        subtitle_enabled=self.subtitle_var.get(),
                        subtitle_format=self.subtitle_format_var.get(),
                        subtitle_stream_option=self.subtitle_stream_var.get(),
                        preserve_metadata=self.shared_metadata_var.get(),
                        use_gpu=self.use_gpu_var.get(),
                        force_cpu=self.force_cpu_var.get(),
                        selected_gpu=selected_gpu,
                        cancel_event=self.media_cancel_event
                    )
            elif media_type == "image":
                if mode == "single":
                    from os.path import dirname
                    if not output_dir:
                        output_dir = dirname(input_file)
                    summary = self.converter.convert_single_image_file(
                        input_file, output_dir, output_format,
                        quality=self.image_quality_var.get(),
                        cancel_event=self.media_cancel_event
                    )
                else:
                    summary = self.converter.convert_image_files(
                        input_dir, output_dir, input_format, output_format,
                        quality=self.image_quality_var.get(),
                        cancel_event=self.media_cancel_event
                    )
            
            self._log_media_conversion_completion(summary)
            
        except Exception as e:
            self.log_callback(f"Media conversion failed: {str(e)}", "ERROR")
        finally:
            # Update button states
            self.parent.after(0, lambda: self.media_convert_start_btn.configure(state=tk.NORMAL))
            self.parent.after(0, lambda: self.media_convert_stop_btn.configure(state=tk.DISABLED))
    
    def stop_media_conversion(self):
        """Stop media conversion process"""
        if hasattr(self, 'media_conversion_thread') and self.media_conversion_thread.is_alive():
            self.log_callback("Media conversion stop requested", "WARNING")
            self.job_status_var.set("Stop requested...")
            self.media_cancel_event.set()
            self.converter.stop_active_process()
            self.media_convert_stop_btn.configure(state=tk.DISABLED)

    def _log_media_conversion_completion(self, summary):
        """Log final conversion status using converter outcome counters."""
        if not summary:
            self.log_callback("Media conversion completed successfully", "SUCCESS")
            self.job_status_var.set("Completed")
            return

        if summary.get("cancelled"):
            self.job_status_var.set("Cancelled")
            self.log_callback(
                f"Media conversion cancelled ({summary.get('success', 0)} succeeded, "
                f"{summary.get('failed', 0)} failed)",
                "WARNING",
            )
        elif summary.get("failed"):
            self.job_status_var.set("Completed with failures")
            self.log_callback(
                f"Media conversion completed with {summary['failed']} failure(s) "
                f"and {summary.get('success', 0)} success(es)",
                "WARNING",
            )
        else:
            self.job_status_var.set("Completed")
            self.log_callback("Media conversion completed successfully", "SUCCESS")
