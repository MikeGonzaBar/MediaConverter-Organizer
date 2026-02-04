"""
Media Converter Page Module
Refactored to use a tabbed interface per media type (Audio, Image, Video).
Each tab maintains its own configuration. The currently selected tab is treated
as the active media type when running conversions.
"""

import tkinter as tk
from tkinter import ttk, filedialog
import threading
from src.media_converter import MediaConverter
from src.ui_components import TooltipManager
from src.gui_utils import WindowManager


class MediaConverterPage:
    """Creates the Media Converter page with per-media-type tabs"""
    
    def __init__(self, parent, log_callback, theme_manager):
        self.parent = parent
        self.log_callback = log_callback
        self.theme_manager = theme_manager
        self.converter = MediaConverter(log_callback)
        
        # Per-tab state containers and widgets
        # Keep variables isolated for each media type
        self.tab_vars = {
            "audio": {
                "media_type": "audio",
                "input_dir_var": tk.StringVar(),
                "input_file_var": tk.StringVar(),
                "input_mode_var": tk.StringVar(value="directory"),
                "output_dir_var": tk.StringVar(),
                "input_format_var": tk.StringVar(),
                "output_format_var": tk.StringVar(),
                # Quality / Advanced
                "audio_quality_var": tk.StringVar(value="high"),
                "audio_codec_var": tk.StringVar(value="aac"),
                "shared_metadata_var": tk.BooleanVar(value=True),
                # UI helpers
                "output_dir_manually_set": False,
            },
            "image": {
                "media_type": "image",
                "input_dir_var": tk.StringVar(),
                "input_file_var": tk.StringVar(),
                "input_mode_var": tk.StringVar(value="directory"),
                "output_dir_var": tk.StringVar(),
                "input_format_var": tk.StringVar(),
                "output_format_var": tk.StringVar(),
                # Quality
                "image_quality_var": tk.StringVar(value="high"),
                # UI helpers
                "output_dir_manually_set": False,
            },
            "video": {
                "media_type": "video",
                "input_dir_var": tk.StringVar(),
                "input_file_var": tk.StringVar(),
                "input_mode_var": tk.StringVar(value="directory"),
                "output_dir_var": tk.StringVar(),
                "input_format_var": tk.StringVar(),
                "output_format_var": tk.StringVar(),
                # Quality / Advanced
                "video_quality_var": tk.StringVar(value="source"),
                "framerate_var": tk.StringVar(value="source"),
                "video_codec_var": tk.StringVar(value="h264"),
                "audio_codec_var": tk.StringVar(value="aac"),
                "subtitle_var": tk.BooleanVar(value=False),
                "subtitle_format_var": tk.StringVar(value="srt"),
                "subtitle_stream_var": tk.StringVar(value="first"),
                "audio_stream_var": tk.StringVar(value="first"),
                "shared_metadata_var": tk.BooleanVar(value=True),
                # GPU
                "use_gpu_var": tk.BooleanVar(value=True),
                "force_cpu_var": tk.BooleanVar(value=False),
                "selected_gpu_var": tk.StringVar(value="auto (Auto-select best GPU)"),
                # UI helpers
                "output_dir_manually_set": False,
            },
        }

        # UI mode options (global toggle that affects visibility in all tabs)
        self.simple_mode_var = tk.BooleanVar(value=True)

        # Holder for per-tab widget references used for visibility updates
        self.tab_ui = {"audio": {}, "image": {}, "video": {}}
    
    def create_page(self):
        """Create the comprehensive Media Converter page"""
        page = ttk.Frame(self.parent, style='Content.TFrame')

        # Page title
        title_label = ttk.Label(page, text="🔄 Media Converter", style='Title.TLabel')
        title_label.pack(pady=(0, 20))

        # Simple Mode toggle (global)
        mode_frame = ttk.Frame(page)
        mode_frame.pack(fill=tk.X, pady=(0, 20))

        simple_mode_checkbox = ttk.Checkbutton(
            mode_frame,
            text="🎯 Simple Mode (Format conversion only)",
            variable=self.simple_mode_var,
            command=self.toggle_simple_mode_all_tabs,
        )
        simple_mode_checkbox.pack(side=tk.LEFT)
        TooltipManager.create_tooltip(
            simple_mode_checkbox,
            "Hide advanced options and use optimal settings for format-only conversion",
        )

        self.simple_mode_status = ttk.Label(
            mode_frame,
            text="✅ Using optimal settings for format conversion",
            style="Success.TLabel",
        )
        self.simple_mode_status.pack(side=tk.LEFT, padx=(20, 0))

        # Notebook for tabs per media type
        self.notebook = ttk.Notebook(page)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

        # Build tabs
        self._tab_order = ["audio", "image", "video"]
        for media_type in self._tab_order:
            tab_frame = ttk.Frame(self.notebook)
            self._build_media_tab(tab_frame, media_type)
            label = "🎵 Audio" if media_type == "audio" else ("🖼️ Image" if media_type == "image" else "🎬 Video")
            self.notebook.add(tab_frame, text=label)

        # Actions card (shared, acts on selected tab)
        from ttkbootstrap.scrolled import ScrolledFrame
        # Place actions below notebook to always be visible
        action_container = ttk.Frame(page)
        action_container.pack(fill=tk.X, pady=(12, 0))
        action_card, action_content = WindowManager.create_modern_section(
            action_container, "🚀 Actions", theme_manager=self.theme_manager
        )
        action_card.pack(fill=tk.X, pady=(0, 24), padx=0)

        self.media_convert_start_btn = WindowManager.create_gray_button(
            action_content, text="🚀 Start Conversion", command=self.start_media_conversion
        )
        self.media_convert_start_btn.pack(side=tk.LEFT, padx=(0, 15))

        self.media_convert_stop_btn = WindowManager.create_gray_button(
            action_content, text="⏹️ Stop", command=self.stop_media_conversion, state=tk.DISABLED
        )
        self.media_convert_stop_btn.pack(side=tk.LEFT)

        # Initialize each tab's default options and visibility
        for mt in self._tab_order:
            self.update_format_options_for(mt)
            self.update_source_visibility_for(mt)
            self.update_quality_visibility_for(mt)
            self.update_advanced_visibility_for(mt)

        # Apply simple mode visibility
        self.toggle_simple_mode_all_tabs()

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
            return f"✅ GPU acceleration available: {', '.join(available_gpus)}"
        else:
            return "❌ No GPU acceleration detected - using CPU encoding"
    
    def update_gpu_selection_options_for(self, media_type: str):
        """Update GPU selection dropdown options for video tab"""
        if media_type != "video":
            return
        vars_ = self.tab_vars[media_type]
        ui = self.tab_ui[media_type]

        available_gpus = self.converter.get_available_gpus()

        options = ["auto (Auto-select best GPU)"]
        for gpu in available_gpus:
            options.append(f"{gpu['type']} ({gpu['name']})")

        ui["gpu_menu"]["menu"].delete(0, "end")
        for option in options:
            ui["gpu_menu"]["menu"].add_command(
                label=option, command=tk._setit(vars_["selected_gpu_var"], option)
            )
        if not vars_["selected_gpu_var"].get() or vars_["selected_gpu_var"].get() not in options:
            vars_["selected_gpu_var"].set(options[0])
    
    def update_gpu_selection_visibility_for(self, media_type: str):
        """Update GPU selection visibility based on settings for a tab"""
        if media_type != "video":
            return
        vars_ = self.tab_vars[media_type]
        ui = self.tab_ui[media_type]
        gpu_enabled = vars_["use_gpu_var"].get() and not vars_["force_cpu_var"].get()
        if gpu_enabled:
            ui["gpu_menu"].configure(state="normal")
        else:
            ui["gpu_menu"].configure(state="disabled")
    
    def toggle_simple_mode_all_tabs(self):
        """Toggle between simple and advanced mode for all tabs"""
        is_simple = self.simple_mode_var.get()

        # Show/hide status
        if is_simple:
            if str(self.simple_mode_status.winfo_manager()) == "":
                self.simple_mode_status.pack(side=tk.LEFT, padx=(20, 0))
        else:
            if str(self.simple_mode_status.winfo_manager()) != "":
                self.simple_mode_status.pack_forget()

        # Apply defaults per tab and toggle visibility
        for mt, vars_ in self.tab_vars.items():
            if is_simple:
                # Defaults aimed at format-only conversion
                if mt == "audio":
                    vars_["audio_quality_var"].set("source")
                    vars_["audio_codec_var"].set("aac")
                    vars_["shared_metadata_var"].set(True)
                elif mt == "video":
                    vars_["video_quality_var"].set("source")
                    vars_["framerate_var"].set("source")
                    vars_["video_codec_var"].set("h264")
                    vars_["audio_codec_var"].set("aac")
                    vars_["subtitle_var"].set(False)
                    vars_["shared_metadata_var"].set(True)
                    vars_["use_gpu_var"].set(True)
                    vars_["force_cpu_var"].set(False)
                    vars_["selected_gpu_var"].set("auto (Auto-select best GPU)")
                elif mt == "image":
                    vars_["image_quality_var"].set("high")

            # Update visibility sections for every tab
            self._toggle_tab_advanced_visibility(mt, not is_simple)
    
    def browse_media_input_directory(self, media_type: str):
        """Browse for media input directory for a specific tab"""
        directory = filedialog.askdirectory(title="Select Input Directory")
        if directory:
            vars_ = self.tab_vars[media_type]
            vars_["input_dir_var"].set(directory)
            # Auto-set output directory unless manually set
            if not vars_["output_dir_manually_set"]:
                vars_["output_dir_var"].set(directory)
    
    def browse_media_input_file(self, media_type: str):
        """Browse for a single input file based on media type (tab)"""
        patterns = {
            "audio": [("Audio", "*.wav;*.flac;*.mp3;*.aac;*.ogg;*.m4a;*.wma")],
            "image": [("Images", "*.jpg;*.jpeg;*.png;*.bmp;*.tiff;*.gif;*.webp")],
            "video": [("Videos", "*.mp4;*.avi;*.mkv;*.mov;*.wmv;*.flv;*.webm")],
        }
        file_path = filedialog.askopenfilename(title="Select Input File", filetypes=patterns.get(media_type, [("All", "*.*")]))
        if file_path:
            vars_ = self.tab_vars[media_type]
            vars_["input_file_var"].set(file_path)
            # Auto-set output directory to parent dir unless manually set
            import os
            if not vars_["output_dir_manually_set"]:
                vars_["output_dir_var"].set(os.path.dirname(file_path))
    
    def browse_media_output_directory(self, media_type: str):
        """Browse for media output directory for a specific tab"""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            vars_ = self.tab_vars[media_type]
            vars_["output_dir_var"].set(directory)
            vars_["output_dir_manually_set"] = True
    
    def update_format_options_for(self, media_type: str):
        """Update format options for a particular tab"""
        vars_ = self.tab_vars[media_type]
        ui = self.tab_ui[media_type]

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
        
        # Update menu options
        if media_type in format_options:
            input_opts = format_options[media_type]["input"]
            output_opts = format_options[media_type]["output"]

            ui["input_format_menu"]["menu"].delete(0, "end")
            for opt in input_opts:
                ui["input_format_menu"]["menu"].add_command(
                    label=opt, command=tk._setit(vars_["input_format_var"], opt)
                )

            ui["output_format_menu"]["menu"].delete(0, "end")
            for opt in output_opts:
                ui["output_format_menu"]["menu"].add_command(
                    label=opt, command=tk._setit(vars_["output_format_var"], opt)
                )

            # Set defaults only if not set yet
            if not vars_["input_format_var"].get() and input_opts:
                vars_["input_format_var"].set(input_opts[0])
            if not vars_["output_format_var"].get() and output_opts:
                vars_["output_format_var"].set(output_opts[0])

        # Update visibility of quality settings for the tab
        self.update_quality_visibility_for(media_type)
        self.update_source_visibility_for(media_type)

    def update_source_visibility_for(self, media_type: str):
        """Toggle between directory and single file inputs for a tab"""
        vars_ = self.tab_vars[media_type]
        ui = self.tab_ui[media_type]
        is_directory = vars_["input_mode_var"].get() == "directory"

        # Show/hide directory widgets
        if is_directory:
            ui["dir_widgets"][0].pack(anchor=tk.W, pady=(0, 10))  # label
            ui["dir_widgets"][1].pack(fill=tk.X, pady=(0, 15))  # frame
            ui["file_widgets"][0].pack_forget()  # label
            ui["file_widgets"][1].pack_forget()  # frame
        else:
            ui["dir_widgets"][0].pack_forget()
            ui["dir_widgets"][1].pack_forget()
            ui["file_widgets"][0].pack(anchor=tk.W, pady=(0, 10))
            ui["file_widgets"][1].pack(fill=tk.X, pady=(0, 15))
    
    def on_input_format_change_for(self, media_type: str, *args):
        """Handle input format change to prevent same input/output format for a tab"""
        vars_ = self.tab_vars[media_type]
        ui = self.tab_ui[media_type]
        input_format = vars_["input_format_var"].get()

        # Get available output formats
        format_options = {
            "audio": ["MP3", "AAC", "FLAC", "OGG", "WAV", "M4A", "WMA"],
            "image": ["JPEG", "PNG", "BMP", "TIFF", "WebP", "GIF"],
            "video": ["MP4", "AVI", "MKV", "MOV", "WebM", "FLV"],
        }

        if media_type in format_options:
            available_outputs = [fmt for fmt in format_options[media_type] if fmt != input_format]
            ui["output_format_menu"]["menu"].delete(0, "end")
            for opt in available_outputs:
                ui["output_format_menu"]["menu"].add_command(
                    label=opt, command=tk._setit(vars_["output_format_var"], opt)
                )
            if vars_["output_format_var"].get() == input_format and available_outputs:
                vars_["output_format_var"].set(available_outputs[0])
    
    def update_quality_visibility_for(self, media_type: str):
        """Update visibility of quality settings based on media type for a tab"""
        ui = self.tab_ui[media_type]
        if media_type == "audio":
            if "audio_quality_frame" in ui:
                ui["audio_quality_frame"].pack(fill=tk.X, pady=(0, 15))
            if "video_quality_frame" in ui:
                ui["video_quality_frame"].pack_forget()
            if "image_quality_frame" in ui:
                ui["image_quality_frame"].pack_forget()
        elif media_type == "video":
            if "audio_quality_frame" in ui:
                ui["audio_quality_frame"].pack_forget()
            if "video_quality_frame" in ui:
                ui["video_quality_frame"].pack(fill=tk.X, pady=(0, 15))
            if "image_quality_frame" in ui:
                ui["image_quality_frame"].pack_forget()
        elif media_type == "image":
            if "audio_quality_frame" in ui:
                ui["audio_quality_frame"].pack_forget()
            if "video_quality_frame" in ui:
                ui["video_quality_frame"].pack_forget()
            if "image_quality_frame" in ui:
                ui["image_quality_frame"].pack(fill=tk.X, pady=(0, 0))

        self.update_advanced_visibility_for(media_type)
    
    def update_advanced_visibility_for(self, media_type: str):
        """Update visibility of advanced options based on media type for a tab"""
        ui = self.tab_ui[media_type]
        if media_type == "audio":
            if "audio_encoding_frame" in ui:
                ui["audio_encoding_frame"].pack(fill=tk.X, pady=(0, 15))
            if "video_encoding_frame" in ui:
                ui["video_encoding_frame"].pack_forget()
            if "subtitle_frame" in ui:
                ui["subtitle_frame"].pack_forget()
            if "metadata_frame" in ui:
                ui["metadata_frame"].pack(fill=tk.X, pady=(0, 0))
        elif media_type == "video":
            if "video_encoding_frame" in ui:
                ui["video_encoding_frame"].pack(fill=tk.X, pady=(0, 15))
            if "audio_encoding_frame" in ui:
                ui["audio_encoding_frame"].pack(fill=tk.X, pady=(0, 15))
            if "subtitle_frame" in ui:
                ui["subtitle_frame"].pack(fill=tk.X, pady=(0, 15))
            if "metadata_frame" in ui:
                ui["metadata_frame"].pack(fill=tk.X, pady=(0, 0))
        elif media_type == "image":
            if "video_encoding_frame" in ui:
                ui["video_encoding_frame"].pack_forget()
            if "audio_encoding_frame" in ui:
                ui["audio_encoding_frame"].pack_forget()
            if "subtitle_frame" in ui:
                ui["subtitle_frame"].pack_forget()
            if "metadata_frame" in ui:
                ui["metadata_frame"].pack_forget()

    def _toggle_tab_advanced_visibility(self, media_type: str, show: bool):
        """Helper to show/hide quality and advanced cards based on simple mode"""
        ui = self.tab_ui[media_type]
        # Quality card
        if show:
            ui["quality_card"].pack(fill=tk.X, pady=(0, 24), padx=0)
            if "advanced_card" in ui:
                ui["advanced_card"].pack(fill=tk.X, pady=(0, 24), padx=0)
        else:
            ui["quality_card"].pack_forget()
            if "advanced_card" in ui:
                ui["advanced_card"].pack_forget()
    
    def start_media_conversion(self):
        """Start media conversion process"""
        media_type = self.get_selected_media_type()
        vars_ = self.tab_vars[media_type]
        mode = vars_["input_mode_var"].get()
        
        # Validate inputs based on mode
        if mode == "directory":
            if not vars_["input_dir_var"].get():
                self.log_callback("Please select an input directory", "ERROR")
                return
        else:  # single file mode
            if not vars_["input_file_var"].get():
                self.log_callback("Please select an input file", "ERROR")
                return
        if not vars_["output_dir_var"].get():
            self.log_callback("Please select an output directory", "ERROR")
            return
        input_format = vars_["input_format_var"].get()
        output_format = vars_["output_format_var"].get()
        
        if input_format == output_format:
            self.log_callback("Input and output formats cannot be the same", "ERROR")
            return
        
        # Update button states
        self.media_convert_start_btn.configure(state=tk.DISABLED)
        self.media_convert_stop_btn.configure(state=tk.NORMAL)
        
        # Start conversion in a separate thread
        self.media_conversion_thread = threading.Thread(target=self.run_media_conversion)
        self.media_conversion_thread.daemon = True
        self.media_conversion_thread.start()
    
    def run_media_conversion(self):
        """Run the media conversion process"""
        try:
            media_type = self.get_selected_media_type()
            vars_ = self.tab_vars[media_type]
            input_dir = vars_["input_dir_var"].get()
            input_file = vars_["input_file_var"].get()
            mode = vars_["input_mode_var"].get()
            output_dir = vars_["output_dir_var"].get()
            input_format = vars_["input_format_var"].get().lower()
            output_format = vars_["output_format_var"].get().lower()
            
            self.log_callback(f"Starting {media_type} conversion from {input_format} to {output_format}", "INFO")
            
            # Build conversion parameters
            if media_type == "audio":
                if mode == "single":
                    from os.path import dirname
                    if not output_dir:
                        output_dir = dirname(input_file)
                    # For single file conversion, let the converter determine the appropriate codec
                    # based on the output format rather than using the GUI codec selection
                    self.converter.convert_single_audio_file(
                        input_file,
                        output_dir,
                        output_format,
                        quality=vars_["audio_quality_var"].get(),
                        audio_codec=None,  # Let the method determine the correct codec
                        preserve_metadata=vars_["shared_metadata_var"].get(),
                    )
                else:
                    self.converter.convert_audio_files(
                        input_dir,
                        output_dir,
                        input_format,
                        output_format,
                        quality=vars_["audio_quality_var"].get(),
                        audio_codec=vars_["audio_codec_var"].get(),
                        preserve_metadata=vars_["shared_metadata_var"].get(),
                    )
            elif media_type == "video":
                if mode == "single":
                    from os.path import dirname
                    if not output_dir:
                        output_dir = dirname(input_file)
                    # Get selected GPU
                    selected_gpu = None
                    if vars_["use_gpu_var"].get() and not vars_["force_cpu_var"].get():
                        gpu_selection = vars_["selected_gpu_var"].get()
                        if gpu_selection and gpu_selection != "auto (Auto-select best GPU)":
                            selected_gpu = gpu_selection.split(" ")[0]  # Extract GPU type
                    
                    self.converter.convert_single_video_file(
                        input_file,
                        output_dir,
                        output_format,
                        quality=vars_["video_quality_var"].get(),
                        framerate=vars_["framerate_var"].get(),
                        video_codec=vars_["video_codec_var"].get(),
                        audio_codec=vars_["audio_codec_var"].get(),
                        preserve_metadata=vars_["shared_metadata_var"].get(),
                        use_gpu=vars_["use_gpu_var"].get(),
                        force_cpu=vars_["force_cpu_var"].get(),
                        selected_gpu=selected_gpu
                    )
                else:
                    # Get selected GPU
                    selected_gpu = None
                    if vars_["use_gpu_var"].get() and not vars_["force_cpu_var"].get():
                        gpu_selection = vars_["selected_gpu_var"].get()
                        if gpu_selection and gpu_selection != "auto (Auto-select best GPU)":
                            selected_gpu = gpu_selection.split(" ")[0]  # Extract GPU type
                    
                    self.converter.convert_video_files(
                        input_dir,
                        output_dir,
                        input_format,
                        output_format,
                        quality=vars_["video_quality_var"].get(),
                        framerate=vars_["framerate_var"].get(),
                        video_codec=vars_["video_codec_var"].get(),
                        audio_codec=vars_["audio_codec_var"].get(),
                        audio_stream_option=vars_["audio_stream_var"].get(),
                        subtitle_enabled=vars_["subtitle_var"].get(),
                        subtitle_format=vars_["subtitle_format_var"].get(),
                        subtitle_stream_option=vars_["subtitle_stream_var"].get(),
                        preserve_metadata=vars_["shared_metadata_var"].get(),
                        use_gpu=vars_["use_gpu_var"].get(),
                        force_cpu=vars_["force_cpu_var"].get(),
                        selected_gpu=selected_gpu
                    )
            elif media_type == "image":
                if mode == "single":
                    from os.path import dirname
                    if not output_dir:
                        output_dir = dirname(input_file)
                    self.converter.convert_single_image_file(
                        input_file,
                        output_dir,
                        output_format,
                        quality=self.tab_vars["image"]["image_quality_var"].get(),
                    )
                else:
                    self.converter.convert_image_files(
                        input_dir,
                        output_dir,
                        input_format,
                        output_format,
                        quality=self.tab_vars["image"]["image_quality_var"].get(),
                    )
            
            self.log_callback("Media conversion completed successfully", "SUCCESS")
            
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
        
        # Update button states
        self.media_convert_start_btn.configure(state=tk.NORMAL)
        self.media_convert_stop_btn.configure(state=tk.DISABLED)

    # -------- Tab building and helpers ---------

    def _build_media_tab(self, parent: ttk.Frame, media_type: str):
        """Builds the UI for a specific media type tab"""
        from ttkbootstrap.scrolled import ScrolledFrame
        scrollable = ScrolledFrame(parent, autohide=True, bootstyle="dark")
        scrollable.pack(fill=tk.BOTH, expand=True)
        try:
            WindowManager.bind_mousewheel(scrollable, None)
        except Exception:
            pass

        ui = {}
        vars_ = self.tab_vars[media_type]

        # IO Section
        io_card, io_content = WindowManager.create_modern_section(
            scrollable, "📂 Input & Output", theme_manager=self.theme_manager
        )
        io_card.pack(fill=tk.X, pady=(0, 24), padx=0)

        mode_frame = ttk.Frame(io_content)
        mode_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Radiobutton(
            mode_frame,
            text="📁 Directory Mode",
            variable=vars_["input_mode_var"],
            value="directory",
            command=lambda mt=media_type: self.update_source_visibility_for(mt),
        ).pack(side=tk.LEFT, padx=(0, 15))
        ttk.Radiobutton(
            mode_frame,
            text="🎵 Single File Mode" if media_type == "audio" else ("🖼️ Single File Mode" if media_type == "image" else "🎬 Single File Mode"),
            variable=vars_["input_mode_var"],
            value="single",
            command=lambda mt=media_type: self.update_source_visibility_for(mt),
        ).pack(side=tk.LEFT)

        # Input dir widgets
        input_dir_label = ttk.Label(
            io_content,
            text="📁 Input Directory:",
            style="Info.TLabel",
        )
        input_frame = ttk.Frame(io_content)
        input_entry = ttk.Entry(
            input_frame, textvariable=vars_["input_dir_var"], width=60, font=("Segoe UI", 10)
        )
        input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 15))
        input_browse_btn = WindowManager.create_gray_button(
            input_frame,
            text="📁 Browse",
            command=lambda mt=media_type: self.browse_media_input_directory(mt),
        )
        input_browse_btn.pack(side=tk.RIGHT)

        # Single file widgets
        input_file_label = ttk.Label(
            io_content,
            text=("🎵 Input File:" if media_type == "audio" else ("🖼️ Input File:" if media_type == "image" else "🎬 Input File:")),
            style="Info.TLabel",
        )
        input_file_frame = ttk.Frame(io_content)
        input_file_entry = ttk.Entry(
            input_file_frame, textvariable=vars_["input_file_var"], width=60, font=("Segoe UI", 10)
        )
        input_file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 15))
        input_file_btn = WindowManager.create_gray_button(
            input_file_frame,
            text=("🎵 Browse File" if media_type == "audio" else ("🖼️ Browse File" if media_type == "image" else "🎬 Browse File")),
            command=lambda mt=media_type: self.browse_media_input_file(mt),
        )
        input_file_btn.pack(side=tk.RIGHT)

        # Output directory
        output_frame = ttk.Frame(io_content)
        output_frame.pack(fill=tk.X, pady=(0, 0))
        ttk.Label(output_frame, text="📁 Output Directory:", style="Info.TLabel").pack(anchor=tk.W)
        output_entry = ttk.Entry(
            output_frame, textvariable=vars_["output_dir_var"], width=60, font=("Segoe UI", 10)
        )
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 15))
        output_browse_btn = WindowManager.create_gray_button(
            output_frame,
            text="📁 Browse",
            command=lambda mt=media_type: self.browse_media_output_directory(mt),
        )
        output_browse_btn.pack(side=tk.RIGHT)

        # Save references
        ui["dir_widgets"] = [input_dir_label, input_frame]
        ui["file_widgets"] = [input_file_label, input_file_frame]

        # Format Section
        format_card, format_content = WindowManager.create_modern_section(
            scrollable, "📋 Format Selection", theme_manager=self.theme_manager
        )
        format_card.pack(fill=tk.X, pady=(0, 24), padx=0)
        # Input format
        input_format_frame = ttk.Frame(format_content)
        input_format_frame.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(input_format_frame, text="📥 Input Format:", style="Info.TLabel").pack(anchor=tk.W, pady=(0, 5))
        input_format_menu = ttk.OptionMenu(input_format_frame, vars_["input_format_var"], None)
        input_format_menu.pack(fill=tk.X, pady=(0, 0))
        vars_["input_format_var"].trace_add(
            "write", lambda *args, mt=media_type: self.on_input_format_change_for(mt)
        )
        # Output format
        output_format_frame = ttk.Frame(format_content)
        output_format_frame.pack(fill=tk.X, pady=(0, 0))
        ttk.Label(output_format_frame, text="📤 Output Format:", style="Info.TLabel").pack(anchor=tk.W, pady=(0, 5))
        output_format_menu = ttk.OptionMenu(output_format_frame, vars_["output_format_var"], None)
        output_format_menu.pack(fill=tk.X, pady=(0, 0))

        ui["input_format_menu"] = input_format_menu
        ui["output_format_menu"] = output_format_menu

        # Quality Section
        quality_card, quality_content = WindowManager.create_modern_section(
            scrollable, "⚙️ Quality Settings", theme_manager=self.theme_manager
        )
        quality_card.pack(fill=tk.X, pady=(0, 24), padx=0)
        ui["quality_card"] = quality_card

        if media_type == "audio":
            audio_quality_frame = ttk.Frame(quality_content)
            audio_quality_frame.pack(fill=tk.X, pady=(0, 15))
            ttk.Label(audio_quality_frame, text="🎵 Audio Quality:", style="Info.TLabel").pack(anchor=tk.W, pady=(0, 5))
            ttk.Radiobutton(audio_quality_frame, text="🎯 Source Quality (Keep Original)", variable=vars_["audio_quality_var"], value="source").pack(anchor=tk.W, pady=(0, 5))
            ttk.Radiobutton(audio_quality_frame, text="🎵 High Quality (320 kbps)", variable=vars_["audio_quality_var"], value="high").pack(anchor=tk.W, pady=(0, 5))
            ttk.Radiobutton(audio_quality_frame, text="📱 Standard Quality (192 kbps)", variable=vars_["audio_quality_var"], value="standard").pack(anchor=tk.W, pady=(0, 5))
            ttk.Radiobutton(audio_quality_frame, text="💾 Low Quality (128 kbps)", variable=vars_["audio_quality_var"], value="low").pack(anchor=tk.W, pady=(0, 0))
            ui["audio_quality_frame"] = audio_quality_frame
        elif media_type == "video":
            video_quality_frame = ttk.Frame(quality_content)
            video_quality_frame.pack(fill=tk.X, pady=(0, 15))
            ttk.Label(video_quality_frame, text="🎬 Video Quality:", style="Info.TLabel").pack(anchor=tk.W, pady=(0, 5))
            ttk.Radiobutton(video_quality_frame, text="🎯 Source Resolution (Keep Original)", variable=vars_["video_quality_var"], value="source").pack(anchor=tk.W, pady=(0, 5))
            ttk.Radiobutton(video_quality_frame, text="🎬 8K Ultra (7680x4320)", variable=vars_["video_quality_var"], value="8k").pack(anchor=tk.W, pady=(0, 5))
            ttk.Radiobutton(video_quality_frame, text="🎬 4K Ultra (3840x2160)", variable=vars_["video_quality_var"], value="4k").pack(anchor=tk.W, pady=(0, 5))
            ttk.Radiobutton(video_quality_frame, text="🎬 High Quality (1080p)", variable=vars_["video_quality_var"], value="high").pack(anchor=tk.W, pady=(0, 5))
            ttk.Radiobutton(video_quality_frame, text="📱 Standard Quality (720p)", variable=vars_["video_quality_var"], value="standard").pack(anchor=tk.W, pady=(0, 5))
            ttk.Radiobutton(video_quality_frame, text="💾 Low Quality (480p)", variable=vars_["video_quality_var"], value="low").pack(anchor=tk.W, pady=(0, 15))
        else:
            # image
            image_quality_frame = ttk.Frame(quality_content)
            image_quality_frame.pack(fill=tk.X, pady=(0, 0))
            ttk.Label(image_quality_frame, text="🖼️ Image Quality:", style="Info.TLabel").pack(anchor=tk.W, pady=(0, 5))
            ttk.Radiobutton(image_quality_frame, text="🎯 Source Quality (Keep Original)", variable=vars_["image_quality_var"], value="source").pack(anchor=tk.W, pady=(0, 5))
            ttk.Radiobutton(image_quality_frame, text="🖼️ High Quality (95%)", variable=vars_["image_quality_var"], value="high").pack(anchor=tk.W, pady=(0, 5))
            ttk.Radiobutton(image_quality_frame, text="📱 Standard Quality (80%)", variable=vars_["image_quality_var"], value="standard").pack(anchor=tk.W, pady=(0, 5))
            ttk.Radiobutton(image_quality_frame, text="💾 Low Quality (60%)", variable=vars_["image_quality_var"], value="low").pack(anchor=tk.W, pady=(0, 0))
            ui["image_quality_frame"] = image_quality_frame
        # Advanced Section: only for audio and video. Omit entirely for image.
        if media_type in ("audio", "video"):
            advanced_card, advanced_content = WindowManager.create_modern_section(
                scrollable, "🔧 Advanced Options", theme_manager=self.theme_manager
            )
            advanced_card.pack(fill=tk.X, pady=(0, 24), padx=0)
            ui["advanced_card"] = advanced_card

            # Shared metadata for audio/video
            metadata_frame = ttk.Frame(advanced_content)
            metadata_frame.pack(fill=tk.X, pady=(0, 0))
            ttk.Checkbutton(
                metadata_frame,
                text="🏷️ Share metadata between audio and video",
                variable=vars_["shared_metadata_var"],
            ).pack(anchor=tk.W, pady=(0, 15))
            ui["metadata_frame"] = metadata_frame

            # Encoding options
            audio_encoding_frame = ttk.Frame(advanced_content)
            audio_encoding_frame.pack(fill=tk.X, pady=(0, 15))
            ttk.Label(audio_encoding_frame, text="🎵 Audio Encoding:", style="Info.TLabel").pack(anchor=tk.W, pady=(0, 5))
            ttk.Radiobutton(audio_encoding_frame, text="🎵 AAC (Compatible)", variable=vars_["audio_codec_var"], value="aac").pack(anchor=tk.W, pady=(0, 5))
            ttk.Radiobutton(audio_encoding_frame, text="🎵 MP3 (Universal)", variable=vars_["audio_codec_var"], value="mp3").pack(anchor=tk.W, pady=(0, 5))
            ttk.Radiobutton(audio_encoding_frame, text="🎵 Opus (Efficient)", variable=vars_["audio_codec_var"], value="opus").pack(anchor=tk.W, pady=(0, 15))
            if media_type == "video":
                ttk.Label(audio_encoding_frame, text="🎵 Multiple Audio Streams:", style="Info.TLabel").pack(anchor=tk.W, pady=(0, 5))
                ttk.Radiobutton(audio_encoding_frame, text="🎵 Use First Stream Only", variable=vars_["audio_stream_var"], value="first").pack(anchor=tk.W, pady=(0, 5))
                ttk.Radiobutton(audio_encoding_frame, text="🎵 Use All Streams (Separate Files)", variable=vars_["audio_stream_var"], value="all").pack(anchor=tk.W, pady=(0, 5))
                ttk.Radiobutton(audio_encoding_frame, text="🎵 Use Best Quality Stream", variable=vars_["audio_stream_var"], value="best").pack(anchor=tk.W, pady=(0, 5))
                ttk.Radiobutton(audio_encoding_frame, text="🎵 Mix All Streams", variable=vars_["audio_stream_var"], value="mix").pack(anchor=tk.W, pady=(0, 0))
            ui["audio_encoding_frame"] = audio_encoding_frame

            if media_type == "video":
                # Video encoding options
                video_encoding_frame = ttk.Frame(advanced_content)
                video_encoding_frame.pack(fill=tk.X, pady=(0, 15))
                ttk.Label(video_encoding_frame, text="🎬 Video Encoding:", style="Info.TLabel").pack(anchor=tk.W, pady=(0, 5))
                ttk.Radiobutton(video_encoding_frame, text="📹 H.264 (Compatible)", variable=vars_["video_codec_var"], value="h264").pack(anchor=tk.W, pady=(0, 5))
                ttk.Radiobutton(video_encoding_frame, text="📹 H.265 (Efficient)", variable=vars_["video_codec_var"], value="h265").pack(anchor=tk.W, pady=(0, 5))
                ttk.Radiobutton(video_encoding_frame, text="📹 VP9 (Web Optimized)", variable=vars_["video_codec_var"], value="vp9").pack(anchor=tk.W, pady=(0, 0))
                ui["video_encoding_frame"] = video_encoding_frame

                # Subtitle options
                subtitle_frame = ttk.Frame(advanced_content)
                subtitle_frame.pack(fill=tk.X, pady=(0, 15))
                ttk.Checkbutton(subtitle_frame, text="📝 Include Subtitles", variable=vars_["subtitle_var"]).pack(anchor=tk.W, pady=(0, 5))
                subtitle_format_frame = ttk.Frame(subtitle_frame)
                subtitle_format_frame.pack(fill=tk.X, pady=(0, 5))
                srt_radio = ttk.Radiobutton(subtitle_format_frame, text="📝 SRT Format", variable=vars_["subtitle_format_var"], value="srt")
                srt_radio.pack(anchor=tk.W, pady=(0, 5))
                TooltipManager.create_tooltip(srt_radio, "SRT: Simple text-based format with timestamps. Compatible with most players and editing software.")
                vtt_radio = ttk.Radiobutton(subtitle_format_frame, text="📝 VTT Format", variable=vars_["subtitle_format_var"], value="vtt")
                vtt_radio.pack(anchor=tk.W, pady=(0, 5))
                TooltipManager.create_tooltip(vtt_radio, "VTT: WebVTT format with HTML-like styling. Better for web players and modern applications.")
                ttk.Label(subtitle_frame, text="📝 Multiple Subtitle Streams:", style="Info.TLabel").pack(anchor=tk.W, pady=(10, 5))
                ttk.Radiobutton(subtitle_frame, text="📝 Use First Stream Only", variable=vars_["subtitle_stream_var"], value="first").pack(anchor=tk.W, pady=(0, 5))
                ttk.Radiobutton(subtitle_frame, text="📝 Use All Streams (Separate Files)", variable=vars_["subtitle_stream_var"], value="all").pack(anchor=tk.W, pady=(0, 5))
                ttk.Radiobutton(subtitle_frame, text="📝 Use Best Quality Stream", variable=vars_["subtitle_stream_var"], value="best").pack(anchor=tk.W, pady=(0, 0))
                ui["subtitle_frame"] = subtitle_frame

                # GPU options
                gpu_frame = ttk.Frame(advanced_content)
                gpu_frame.pack(fill=tk.X, pady=(0, 0))
                ttk.Label(gpu_frame, text="🎮 GPU Acceleration:", style="Info.TLabel").pack(anchor=tk.W, pady=(0, 5))
                gpu_status = self.get_gpu_status_text()
                ttk.Label(gpu_frame, text=gpu_status, style="Info.TLabel", font=("Segoe UI", 9)).pack(anchor=tk.W, pady=(0, 10))
                gpu_checkbox = ttk.Checkbutton(
                    gpu_frame,
                    text="🚀 Use GPU acceleration (if available)",
                    variable=vars_["use_gpu_var"],
                    command=lambda mt=media_type: self.update_gpu_selection_visibility_for(mt),
                )
                gpu_checkbox.pack(anchor=tk.W, pady=(0, 5))
                TooltipManager.create_tooltip(
                    gpu_checkbox,
                    "Enable GPU acceleration for faster video encoding. Automatically detects and uses NVIDIA, AMD, Intel, or Apple GPU encoders.",
                )
                gpu_selection_frame = ttk.Frame(gpu_frame)
                gpu_selection_frame.pack(fill=tk.X, pady=(0, 5))
                ttk.Label(gpu_selection_frame, text="🎯 GPU Selection:", style="Info.TLabel").pack(side=tk.LEFT, padx=(0, 10))
                gpu_menu = ttk.OptionMenu(gpu_selection_frame, vars_["selected_gpu_var"], None)
                gpu_menu.pack(side=tk.LEFT)
                ui["gpu_menu"] = gpu_menu
                # Ensure self.tab_ui reference is up to date before using helper
                self.tab_ui[media_type] = ui
                self.update_gpu_selection_options_for(media_type)
                cpu_checkbox = ttk.Checkbutton(
                    gpu_frame,
                    text="💻 Force CPU encoding",
                    variable=vars_["force_cpu_var"],
                    command=lambda mt=media_type: self.update_gpu_selection_visibility_for(mt),
                )
                cpu_checkbox.pack(anchor=tk.W, pady=(0, 0))
                TooltipManager.create_tooltip(
                    cpu_checkbox, "Force CPU encoding even if GPU is available. Useful for maximum quality or compatibility."
                )
                ui["gpu_frame"] = gpu_frame

        # Save UI references (ensure stored, even if already set above)
        self.tab_ui[media_type] = ui

        # Initial IO widgets visibility
        self.update_source_visibility_for(media_type)

    def _on_tab_changed(self, event):
        """When switching tabs, ensure each tab's menus/visibility are valid"""
        media_type = self.get_selected_media_type()
        self.update_format_options_for(media_type)
        self.update_source_visibility_for(media_type)
        self.update_quality_visibility_for(media_type)
        self.update_advanced_visibility_for(media_type)
        if media_type == "video":
            self.update_gpu_selection_visibility_for(media_type)

    def get_selected_media_type(self) -> str:
        idx = self.notebook.index(self.notebook.select())
        return self._tab_order[idx]
