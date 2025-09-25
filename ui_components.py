"""
UI Components Module
Contains reusable UI components and page creators
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
import queue
import threading


class TooltipManager:
    """Manages tooltip creation and display"""
    
    @staticmethod
    def create_tooltip(widget, text):
        """Create a tooltip for a widget"""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = tk.Label(tooltip, text=text, background="white", 
                           foreground="#212529", relief="solid", borderwidth=1,
                           font=('Segoe UI', 9), wraplength=300)
            label.pack()
            
            widget.tooltip = tooltip
        
        def hide_tooltip(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
        
        widget.bind('<Enter>', show_tooltip)
        widget.bind('<Leave>', hide_tooltip)


class MediaOrganizerPage:
    """Creates the Media Organizer page"""
    
    def __init__(self, parent, log_callback):
        self.parent = parent
        self.log_callback = log_callback
        self.organize_mode_var = tk.StringVar(value="check")
        self.media_dir_var = tk.StringVar()
    
    def create_page(self):
        """Create the Media Organizer page"""
        page = ttk.Frame(self.parent, style='Content.TFrame')
        
        # Page title
        title_label = ttk.Label(page, text="📁 Media Organizer", style='Title.TLabel')
        title_label.pack(pady=(0, 30))
        
        # Create scrollable content
        canvas = tk.Canvas(page, bg='#f8f9fa', highlightthickness=0)
        scrollbar = ttk.Scrollbar(page, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Content.TFrame')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Directory Selection Card
        dir_card = ttk.LabelFrame(scrollable_frame, text="📂 Directory Selection", padding=20)
        dir_card.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(dir_card, text="📁 Media Directory:", style='Info.TLabel').pack(anchor=tk.W, pady=(0, 10))
        
        dir_frame = ttk.Frame(dir_card)
        dir_frame.pack(fill=tk.X, pady=(0, 0))
        
        dir_entry = ttk.Entry(dir_frame, textvariable=self.media_dir_var, width=60, font=('Segoe UI', 10))
        dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 15))
        
        browse_btn = ttk.Button(dir_frame, text="📁 Browse", command=self.browse_media_directory, style='Primary.TButton')
        browse_btn.pack(side=tk.RIGHT)
        
        # Operation Mode Card
        mode_card = ttk.LabelFrame(scrollable_frame, text="⚙️ Operation Mode", padding=20)
        mode_card.pack(fill=tk.X, pady=(0, 20))
        
        # Check Only option
        check_frame = ttk.Frame(mode_card)
        check_frame.pack(fill=tk.X, pady=(0, 10))
        
        check_radio = ttk.Radiobutton(check_frame, text="🔍 Check Only", variable=self.organize_mode_var, value="check")
        check_radio.pack(side=tk.LEFT)
        TooltipManager.create_tooltip(check_radio, "Only analyze files and show what would be organized without making any changes")
        
        # Dry Run option
        dry_run_frame = ttk.Frame(mode_card)
        dry_run_frame.pack(fill=tk.X, pady=(0, 10))
        
        dry_run_radio = ttk.Radiobutton(dry_run_frame, text="🧪 Dry Run", variable=self.organize_mode_var, value="dry_run")
        dry_run_radio.pack(side=tk.LEFT)
        TooltipManager.create_tooltip(dry_run_radio, "Simulate the organization process and show detailed logs without actually moving files")
        
        # Actually Move Files option
        move_frame = ttk.Frame(mode_card)
        move_frame.pack(fill=tk.X, pady=(0, 0))
        
        move_radio = ttk.Radiobutton(move_frame, text="🚀 Actually Move Files", variable=self.organize_mode_var, value="move")
        move_radio.pack(side=tk.LEFT)
        TooltipManager.create_tooltip(move_radio, "Actually organize files by moving them to appropriate folders based on their metadata")
        
        # Action Card
        action_card = ttk.LabelFrame(scrollable_frame, text="🚀 Actions", padding=20)
        action_card.pack(fill=tk.X, pady=(0, 20))
        
        self.start_btn = ttk.Button(action_card, text="🚀 Start Organization", command=self.start_organization, style='Success.TButton')
        self.start_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        self.stop_btn = ttk.Button(action_card, text="⏹️ Stop", command=self.stop_organization, state=tk.DISABLED, style='Danger.TButton')
        self.stop_btn.pack(side=tk.LEFT)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel to canvas
        from gui_utils import WindowManager
        WindowManager.bind_mousewheel(canvas, scrollbar)
        
        return page
    
    def browse_media_directory(self):
        """Browse for media directory"""
        directory = filedialog.askdirectory(title="Select Media Directory")
        if directory:
            self.media_dir_var.set(directory)
    
    def start_organization(self):
        """Start media organization process"""
        if not self.media_dir_var.get():
            self.log_callback("Please select a media directory", "ERROR")
            return
        
        # Update button states
        self.start_btn.configure(state=tk.DISABLED)
        self.stop_btn.configure(state=tk.NORMAL)
        
        # Start organization in a separate thread
        self.organization_thread = threading.Thread(target=self.run_organization)
        self.organization_thread.daemon = True
        self.organization_thread.start()
    
    def run_organization(self):
        """Run the media organization process"""
        try:
            mode = self.organize_mode_var.get()
            directory = self.media_dir_var.get()
            
            self.log_callback(f"Starting media organization in {mode} mode", "INFO")
            
            # Import and run the appropriate organizer
            if mode == "check":
                from image_organizer import ImageOrganizer
                from video_organizer import VideoOrganizer
                
                # Check images
                img_organizer = ImageOrganizer(directory, mode="check")
                img_organizer.organize_images()
                
                # Check videos
                vid_organizer = VideoOrganizer(directory, mode="check")
                vid_organizer.organize_videos()
                
            elif mode == "dry_run":
                from image_organizer import ImageOrganizer
                from video_organizer import VideoOrganizer
                
                # Dry run images
                img_organizer = ImageOrganizer(directory, mode="dry_run")
                img_organizer.organize_images()
                
                # Dry run videos
                vid_organizer = VideoOrganizer(directory, mode="dry_run")
                vid_organizer.organize_videos()
                
            elif mode == "move":
                from image_organizer import ImageOrganizer
                from video_organizer import VideoOrganizer
                
                # Actually organize images
                img_organizer = ImageOrganizer(directory, mode="move")
                img_organizer.organize_images()
                
                # Actually organize videos
                vid_organizer = VideoOrganizer(directory, mode="move")
                vid_organizer.organize_videos()
            
            self.log_callback("Media organization completed successfully", "SUCCESS")
            
        except Exception as e:
            self.log_callback(f"Media organization failed: {str(e)}", "ERROR")
        finally:
            # Update button states
            self.parent.after(0, lambda: self.start_btn.configure(state=tk.NORMAL))
            self.parent.after(0, lambda: self.stop_btn.configure(state=tk.DISABLED))
    
    def stop_organization(self):
        """Stop media organization process"""
        self.log_callback("Media organization stop requested", "WARNING")
        # Update button states
        self.start_btn.configure(state=tk.NORMAL)
        self.stop_btn.configure(state=tk.DISABLED)


class WAVConverterPage:
    """Creates the WAV to FLAC Converter page"""
    
    def __init__(self, parent, log_callback):
        self.parent = parent
        self.log_callback = log_callback
        self.wav_dir_var = tk.StringVar()
        self.wav_file_var = tk.StringVar()
        self.input_mode_var = tk.StringVar(value="directory")  # directory | single
        self.output_dir_var = tk.StringVar()
        # Track if output dir is being auto-set from input selection
        self._auto_output = True
        self._last_input_based_output = ""
        self.quality_var = tk.StringVar(value="high")
        self.metadata_var = tk.BooleanVar(value=True)
        self.fingerprint_var = tk.BooleanVar(value=False)
    
    def create_page(self):
        """Create the WAV to FLAC Converter page"""
        page = ttk.Frame(self.parent, style='Content.TFrame')
        
        # Page title
        title_label = ttk.Label(page, text="🎵 WAV to FLAC Converter", style='Title.TLabel')
        title_label.pack(pady=(0, 30))
        
        # Create scrollable content
        canvas = tk.Canvas(page, bg='#f8f9fa', highlightthickness=0)
        scrollbar = ttk.Scrollbar(page, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Content.TFrame')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Mode & Source Selection Card
        dir_card = ttk.LabelFrame(scrollable_frame, text="📂 Source Selection", padding=20)
        dir_card.pack(fill=tk.X, pady=(0, 20))
        
        # Mode toggle (Directory vs Single File)
        mode_frame = ttk.Frame(dir_card)
        mode_frame.pack(fill=tk.X, pady=(0, 10))
        
        dir_mode_radio = ttk.Radiobutton(mode_frame, text="📁 Directory Mode", variable=self.input_mode_var, value="directory", command=self._update_source_visibility)
        dir_mode_radio.pack(side=tk.LEFT, padx=(0, 15))
        
        file_mode_radio = ttk.Radiobutton(mode_frame, text="🎵 Single File Mode", variable=self.input_mode_var, value="single", command=self._update_source_visibility)
        file_mode_radio.pack(side=tk.LEFT)
        
        dir_label = ttk.Label(dir_card, text="📁 WAV/FLAC Directory:", style='Info.TLabel')
        dir_label.pack(anchor=tk.W, pady=(0, 10))
        
        dir_frame = ttk.Frame(dir_card)
        dir_frame.pack(fill=tk.X, pady=(0, 0))
        
        dir_entry = ttk.Entry(dir_frame, textvariable=self.wav_dir_var, width=60, font=('Segoe UI', 10))
        dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 15))
        
        browse_btn = ttk.Button(dir_frame, text="📁 Browse", command=self.browse_wav_directory, style='Primary.TButton')
        browse_btn.pack(side=tk.RIGHT)

        # Single file selection (hidden by default)
        self.file_label = ttk.Label(dir_card, text="🎵 WAV/FLAC File:", style='Info.TLabel')
        self.file_frame = ttk.Frame(dir_card)
        
        self.file_entry = ttk.Entry(self.file_frame, textvariable=self.wav_file_var, width=60, font=('Segoe UI', 10))
        self.file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 15))
        
        self.file_browse_btn = ttk.Button(self.file_frame, text="🎵 Browse File", command=self.browse_wav_file, style='Primary.TButton')
        self.file_browse_btn.pack(side=tk.RIGHT)
        
        # Output Directory Card
        out_card = ttk.LabelFrame(scrollable_frame, text="📤 Output Directory", padding=20)
        out_card.pack(fill=tk.X, pady=(0, 20))
        
        out_label = ttk.Label(out_card, text="📁 Target Directory:", style='Info.TLabel')
        out_label.pack(anchor=tk.W, pady=(0, 10))
        
        out_frame = ttk.Frame(out_card)
        out_frame.pack(fill=tk.X)
        
        out_entry = ttk.Entry(out_frame, textvariable=self.output_dir_var, width=60, font=('Segoe UI', 10))
        out_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 15))
        
        out_browse_btn = ttk.Button(out_frame, text="📁 Browse", command=self.browse_output_directory, style='Primary.TButton')
        out_browse_btn.pack(side=tk.RIGHT)

        # Quality Settings Card
        quality_card = ttk.LabelFrame(scrollable_frame, text="⚙️ Quality Settings", padding=20)
        quality_card.pack(fill=tk.X, pady=(0, 20))
        
        # High Quality option
        high_frame = ttk.Frame(quality_card)
        high_frame.pack(fill=tk.X, pady=(0, 10))
        
        high_radio = ttk.Radiobutton(high_frame, text="🎵 High Quality", variable=self.quality_var, value="high")
        high_radio.pack(side=tk.LEFT)
        TooltipManager.create_tooltip(high_radio, "Best quality conversion with maximum compression efficiency")
        
        # Compatibility Mode option
        compat_frame = ttk.Frame(quality_card)
        compat_frame.pack(fill=tk.X, pady=(0, 10))
        
        compat_radio = ttk.Radiobutton(compat_frame, text="📱 Compatibility Mode", variable=self.quality_var, value="compatibility")
        compat_radio.pack(side=tk.LEFT)
        TooltipManager.create_tooltip(compat_radio, "Optimized for maximum compatibility with older players and devices")
        
        # Metadata Options Card
        metadata_card = ttk.LabelFrame(scrollable_frame, text="🏷️ Metadata Options", padding=20)
        metadata_card.pack(fill=tk.X, pady=(0, 20))
        
        # Aggressive metadata search
        aggressive_frame = ttk.Frame(metadata_card)
        aggressive_frame.pack(fill=tk.X, pady=(0, 10))
        
        aggressive_check = ttk.Checkbutton(aggressive_frame, text="🔍 Aggressive metadata search", variable=self.metadata_var)
        aggressive_check.pack(side=tk.LEFT)
        TooltipManager.create_tooltip(aggressive_check, "Search multiple databases for comprehensive metadata information")
        
        # Audio Fingerprinting
        fingerprint_frame = ttk.Frame(metadata_card)
        fingerprint_frame.pack(fill=tk.X, pady=(0, 0))
        
        fingerprint_check = ttk.Checkbutton(fingerprint_frame, text="🎵 Audio Fingerprinting", variable=self.fingerprint_var)
        fingerprint_check.pack(side=tk.LEFT)
        TooltipManager.create_tooltip(fingerprint_check, "Use audio fingerprinting to identify songs and retrieve metadata")
        
        # Action Card
        action_card = ttk.LabelFrame(scrollable_frame, text="🚀 Actions", padding=20)
        action_card.pack(fill=tk.X, pady=(0, 20))
        
        self.start_btn = ttk.Button(action_card, text="🚀 Start Conversion", command=self.start_conversion, style='Success.TButton')
        self.start_btn.pack(side=tk.LEFT, padx=(0, 15))
        
        self.stop_btn = ttk.Button(action_card, text="⏹️ Stop", command=self.stop_conversion, state=tk.DISABLED, style='Danger.TButton')
        self.stop_btn.pack(side=tk.LEFT)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel to canvas
        from gui_utils import WindowManager
        WindowManager.bind_mousewheel(canvas, scrollbar)
        
        # Initial visibility for source inputs (toggle frames/labels, not inner widgets)
        self._dir_widgets = [dir_label, dir_frame]
        self._file_widgets = [self.file_label, self.file_frame]
        self._update_source_visibility()

        return page
    
    def browse_wav_directory(self):
        """Browse for WAV directory"""
        directory = filedialog.askdirectory(title="Select WAV/FLAC Directory")
        if directory:
            self.wav_dir_var.set(directory)
            # Default output to the same folder unless user chose a custom one
            if self._auto_output or not self.output_dir_var.get() or self.output_dir_var.get() == self._last_input_based_output:
                self.output_dir_var.set(directory)
                self._last_input_based_output = directory
    
    def browse_wav_file(self):
        """Browse for a single WAV/FLAC file"""
        filetypes = [
            ("Audio Files", "*.wav;*.flac"),
            ("WAV", "*.wav"),
            ("FLAC", "*.flac"),
            ("All Files", "*.*")
        ]
        file_path = filedialog.askopenfilename(title="Select WAV/FLAC File", filetypes=filetypes)
        if file_path:
            self.wav_file_var.set(file_path)
            # Default output to the file's folder unless user chose a custom one
            try:
                import os
                parent_dir = os.path.dirname(file_path)
                if self._auto_output or not self.output_dir_var.get() or self.output_dir_var.get() == self._last_input_based_output:
                    self.output_dir_var.set(parent_dir)
                    self._last_input_based_output = parent_dir
            except Exception:
                pass
    
    def browse_output_directory(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir_var.set(directory)
            # User explicitly selected output, stop auto-updating
            self._auto_output = False
    
    def _update_source_visibility(self):
        """Toggle visibility of directory vs file inputs based on mode"""
        is_directory = self.input_mode_var.get() == "directory"
        
        # Show/hide directory widgets
        if is_directory:
            # Show directory widgets
            self._dir_widgets[0].pack(anchor=tk.W, pady=(0, 10))  # label
            self._dir_widgets[1].pack(fill=tk.X, pady=(0, 0))  # frame containing entry+button
            
            # Hide file widgets
            self._file_widgets[0].pack_forget()  # label
            self._file_widgets[1].pack_forget()  # frame
        else:
            # Hide directory widgets
            self._dir_widgets[0].pack_forget()  # label
            self._dir_widgets[1].pack_forget()  # frame
            
            # Show file widgets
            self._file_widgets[0].pack(anchor=tk.W, pady=(0, 10))  # label
            self._file_widgets[1].pack(fill=tk.X, pady=(0, 0))  # frame containing entry+button
    
    def start_conversion(self):
        """Start WAV to FLAC conversion process"""
        mode = self.input_mode_var.get()
        
        if mode == "directory" and not self.wav_dir_var.get():
            self.log_callback("Please select a WAV/FLAC directory", "ERROR")
            return
        elif mode == "single" and not self.wav_file_var.get():
            self.log_callback("Please select a WAV/FLAC file", "ERROR")
            return
        
        # Validate output directory
        output_dir = self.output_dir_var.get()
        if not output_dir:
            self.log_callback("Please select an output directory", "ERROR")
            return
        
        # Update button states
        self.start_btn.configure(state=tk.DISABLED)
        self.stop_btn.configure(state=tk.NORMAL)
        
        # Start conversion in a separate thread
        self.conversion_thread = threading.Thread(target=self.run_conversion)
        self.conversion_thread.daemon = True
        self.conversion_thread.start()
    
    def run_conversion(self):
        """Run the WAV to FLAC conversion process"""
        try:
            mode = self.input_mode_var.get()
            directory = self.wav_dir_var.get()
            single_file = self.wav_file_var.get()
            output_dir = self.output_dir_var.get()
            quality = self.quality_var.get()
            metadata = self.metadata_var.get()
            fingerprint = self.fingerprint_var.get()
            
            self.log_callback(f"Starting WAV to FLAC conversion in {quality} mode", "INFO")
            
            # Use enhanced converter (directory or single file)
            from wav_to_flac_converter import EnhancedWAVToFLACConverter
            
            # Decide source path for converter
            if mode == "single":
                if not single_file:
                    self.log_callback("Please select a WAV/FLAC file", "ERROR")
                    return
                import os
                source_path = os.path.dirname(single_file)
            else:
                if not directory:
                    self.log_callback("Please select a WAV/FLAC directory", "ERROR")
                    return
                source_path = directory
            
            converter = EnhancedWAVToFLACConverter(
                source_path=source_path,
                output_folder=output_dir,
                compatibility_mode=(quality == "compatibility"),
                enable_metadata=metadata,
                aggressive_metadata=metadata,
                enable_fingerprinting=fingerprint
            )
            
            if mode == "single":
                from pathlib import Path
                success = converter.process_single_file(Path(single_file))
                if not success:
                    raise RuntimeError("Single file conversion failed")
            else:
                converter.convert_all()
            
            self.log_callback("WAV to FLAC conversion completed successfully", "SUCCESS")
            
        except Exception as e:
            self.log_callback(f"WAV to FLAC conversion failed: {str(e)}", "ERROR")
        finally:
            # Update button states
            self.parent.after(0, lambda: self.start_btn.configure(state=tk.NORMAL))
            self.parent.after(0, lambda: self.stop_btn.configure(state=tk.DISABLED))
    
    def stop_conversion(self):
        """Stop WAV to FLAC conversion process"""
        self.log_callback("WAV to FLAC conversion stop requested", "WARNING")
        # Update button states
        self.start_btn.configure(state=tk.NORMAL)
        self.stop_btn.configure(state=tk.DISABLED)
