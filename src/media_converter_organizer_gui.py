"""
Media Converter & Organizer GUI - Refactored Version
Main application file with modular architecture
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from datetime import datetime
import queue
import threading
import platform

# Import our custom modules
from src.gui_utils import WindowManager, LogManager, NavigationManager
from src.ui_components import MediaOrganizerPage
from src.media_converter_page import MediaConverterPage

# Try to import dependency checker (optional)
try:
    from src.dependency_checker import DependencyChecker
    DEPENDENCY_CHECKER_AVAILABLE = True
except ImportError:
    DEPENDENCY_CHECKER_AVAILABLE = False
    DEPENDENCY_CHECKER_AVAILABLE = False


class MediaConverterOrganizerGUI:
    """Main GUI application class"""
    
    def __init__(self):
        WindowManager.set_process_app_id()
        self.root = tk.Tk()
        self.setup_window()
        self.setup_styles()
        self.setup_logging()
        self.setup_navigation()
        self.setup_pages()
        self.setup_event_handlers()
    
    def setup_window(self):
        """Setup main window properties with Windows 11 styling"""
        self.root.title("Media Converter & Organizer")
        # Widen the window to accommodate a right-side logs panel
        WindowManager.center_window(self.root, width=1400, height=800)
        self.root.minsize(1200, 700)
        
        # Windows 11 dark theme window styling
        if platform.system() == "Windows":
            try:
                # Set window background to Windows 11 dark theme
                self.root.configure(bg='#202020')  # Windows 11 dark background
                
                # Try to set window to use Windows 11 rounded corners (Windows 11 only)
                # This requires Windows 11 build 22000+
                try:
                    import ctypes
                    # DWMWA_WINDOW_CORNER_PREFERENCE = 33
                    # DWMWCP_ROUND = 2
                    DWMWA_WINDOW_CORNER_PREFERENCE = 33
                    DWMWCP_ROUND = 2
                    hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
                    ctypes.windll.dwmapi.DwmSetWindowAttribute(
                        hwnd,
                        DWMWA_WINDOW_CORNER_PREFERENCE,
                        ctypes.byref(ctypes.c_int(DWMWCP_ROUND)),
                        ctypes.sizeof(ctypes.c_int)
                    )
                except:
                    pass  # Not Windows 11 or feature not available
            except:
                pass
        
        WindowManager.set_window_icon(self.root)
    
    def setup_styles(self):
        """Setup application styles"""
        self.style = WindowManager.setup_styles()
    
    def setup_logging(self):
        """Setup logging system"""
        self.log_manager = LogManager()
        self.dependency_warnings = []
        self._check_dependencies()
    
    def _check_dependencies(self):
        """Check dependencies and log warnings"""
        if DEPENDENCY_CHECKER_AVAILABLE:
            try:
                checker = DependencyChecker()
                status = checker.check_all()
                
                # Log FFmpeg status
                if not status['ffmpeg']:
                    system = platform.system()
                    install_cmd = {
                        "Windows": "winget install ffmpeg",
                        "Darwin": "brew install ffmpeg",
                        "Linux": "sudo apt install ffmpeg"
                    }.get(system, "See documentation")
                    self.log_manager.log_message(
                        f"FFmpeg not found. Install with: {install_cmd}",
                        "WARNING"
                    )
                    self.dependency_warnings.append(f"FFmpeg not found. Install with: {install_cmd}")
                
                # Log fpcalc status (optional)
                if not status['fpcalc']:
                    self.log_manager.log_message(
                        "Chromaprint (fpcalc) not found. Audio fingerprinting will be disabled.",
                        "WARNING"
                    )
                
                # Log Python packages
                required, optional = status['python_packages']
                if required:
                    self.log_manager.log_message(
                        f"Missing required packages: {', '.join(required)}. Install with: pip install {' '.join(required)}",
                        "WARNING"
                    )
                    self.dependency_warnings.append(
                        f"Missing packages: {', '.join(required)}. Install with: pip install {' '.join(required)}"
                    )
            except Exception:
                # Silently fail if dependency checker has issues
                pass
    
    def setup_navigation(self):
        """Setup sidebar navigation"""
        # Create main container
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create navigation manager
        self.nav_manager = NavigationManager(self.main_container, None, {})
        
        # Create sidebar
        self.sidebar = self.nav_manager.create_sidebar()

        self.logs_restore_panel = tk.Frame(self.main_container, bg='#1C1C1C', width=88)
        self.logs_restore_panel.pack_propagate(False)
        restore_btn = tk.Button(
            self.logs_restore_panel,
            text="Logs",
            command=self.toggle_logs_panel,
            font=('Segoe UI', 10, 'bold'),
            bg='#2D2D2D',
            fg='#FFFFFF',
            activebackground='#3A3A3A',
            activeforeground='#FFFFFF',
            relief='flat',
            borderwidth=0,
            padx=10,
            pady=10,
            cursor='hand2',
        )
        restore_btn.pack(fill=tk.X, padx=10, pady=18)
        
        # Create a paned window for resizable content and logs panels
        # Users can drag the sash (divider) to resize the Activity Log panel
        self.paned_window = ttk.PanedWindow(self.main_container, orient=tk.HORIZONTAL)
        self.paned_window.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Content area (left side of paned window)
        self.content_area = ttk.Frame(self.paned_window, style='Content.TFrame')
        self.paned_window.add(self.content_area, weight=5)  # Give the primary workflow more room
        
        # Persistent logs panel on the right (resizable) - Windows 11 dark theme
        self.logs_panel = tk.Frame(self.paned_window, bg='#1C1C1C')  # Windows 11 dark background
        self.paned_window.add(self.logs_panel, weight=2)  # Logs start useful but secondary
        self.logs_collapsed = False
        
        # Configure the paned window after adding all panes
        self.configure_paned_window()
        
        # Logs header with title and clear button
        logs_header = tk.Frame(self.logs_panel, bg='#1C1C1C')
        logs_header.pack(fill=tk.X, padx=20, pady=(16, 0))
        
        self.logs_toggle_btn = tk.Button(
            logs_header,
            text="Hide",
            font=('Segoe UI', 9),
            bg='#2D2D2D',
            fg='#FFFFFF',
            activebackground='#3A3A3A',
            activeforeground='#FFFFFF',
            relief='flat',
            borderwidth=0,
            padx=9,
            pady=5,
            cursor='hand2',
            command=self.toggle_logs_panel
        )
        self.logs_toggle_btn.pack(side=tk.RIGHT, padx=(8, 0))

        logs_title = tk.Label(
            logs_header, 
            text="Activity Logs",
            font=('Segoe UI', 13, 'bold'),
            bg='#1C1C1C',
            fg='#FFFFFF',
            anchor='w'
        )
        logs_title.pack(side=tk.LEFT)
        
        # Clear logs button - Gray button style
        clear_logs_btn = tk.Button(
            logs_header,
            text="Clear",
            font=('Segoe UI', 9),
            bg='#4A4A4A',  # Gray background
            fg='#FFFFFF',  # White text
            activebackground='#3A3A3A',  # Darker gray when pressed
            activeforeground='#FFFFFF',
            relief='solid',
            borderwidth=1,
            highlightthickness=0,
            highlightbackground='#3D3D3D',
            highlightcolor='#0078D4',
            padx=10,
            pady=5,
            cursor='hand2',
            command=self.clear_logs
        )
        # Add hover effect - lighter gray with darker white text
        def on_clear_enter(e):
            clear_logs_btn.config(bg='#5A5A5A', fg='#E0E0E0', highlightbackground='#5A5A5A')
        def on_clear_leave(e):
            clear_logs_btn.config(bg='#4A4A4A', fg='#FFFFFF', highlightbackground='#3D3D3D')
        clear_logs_btn.bind('<Enter>', on_clear_enter)
        clear_logs_btn.bind('<Leave>', on_clear_leave)
        clear_logs_btn.pack(side=tk.RIGHT)

        self.logs_body = tk.Frame(self.logs_panel, bg='#1C1C1C')
        self.logs_body.pack(fill=tk.BOTH, expand=True)

        filters_frame = tk.Frame(self.logs_body, bg='#1C1C1C')
        filters_frame.pack(fill=tk.X, padx=20, pady=(12, 0))

        self.log_filter_vars = {}
        for label, level in (("Info", "INFO"), ("Success", "SUCCESS"), ("Warn", "WARNING"), ("Error", "ERROR")):
            var = tk.BooleanVar(value=True)
            self.log_filter_vars[level] = var
            check = tk.Checkbutton(
                filters_frame,
                text=label,
                variable=var,
                command=lambda lvl=level, v=var: self.log_manager.set_level_visible(lvl, v.get()),
                bg='#1C1C1C',
                fg='#C0C0C0',
                activebackground='#1C1C1C',
                activeforeground='#FFFFFF',
                selectcolor='#2D2D2D',
                font=('Segoe UI', 9),
                bd=0,
                highlightthickness=0,
            )
            check.pack(side=tk.LEFT, padx=(0, 10))
        
        # Subtle separator line
        logs_separator = tk.Frame(self.logs_body, bg='#3D3D3D', height=1)
        logs_separator.pack(fill=tk.X, padx=20, pady=(12, 12))
        
        # Log display widget - Windows 11 dark theme
        from tkinter import scrolledtext
        self.side_log_text = scrolledtext.ScrolledText(
            self.logs_body,
            wrap=tk.WORD,
            font=('Consolas', 9),
            bg='#1C1C1C',  # Windows 11 dark background
            fg='#FFFFFF',  # White text
            insertbackground='#0078D4',  # Accent blue cursor
            selectbackground='#0078D4',  # Accent blue selection
            borderwidth=1,
            highlightthickness=0,
            relief='solid',
            highlightbackground='#3D3D3D',
            highlightcolor='#0078D4',
            spacing1=2,
            spacing2=1,
            spacing3=2
        )
        self.side_log_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Wire the LogManager to the side panel and start queue checking
        self.log_manager.log_widget = self.side_log_text
        self.log_manager.check_queue()
        
        # Update navigation manager with content area
        self.nav_manager.content_area = self.content_area
    
    def clear_logs(self):
        """Clear all activity logs"""
        if self.side_log_text:
            self.log_manager.entries.clear()
            self.side_log_text.delete(1.0, tk.END)
            self.log_manager.log_message("Logs cleared", "INFO")

    def toggle_logs_panel(self):
        """Collapse or expand the Activity Logs panel."""
        self.logs_collapsed = not self.logs_collapsed
        if self.logs_collapsed:
            self.paned_window.forget(self.logs_panel)
            self.paned_window.pack_forget()
            self.logs_restore_panel.pack(side=tk.RIGHT, fill=tk.Y)
            self.paned_window.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        else:
            self.logs_toggle_btn.configure(text="Hide")
            self.logs_restore_panel.pack_forget()
            panes = {str(pane) for pane in self.paned_window.panes()}
            if str(self.logs_panel) not in panes:
                self.paned_window.add(self.logs_panel, weight=2)
        self.root.after(50, self._set_initial_sash_position)
    
    def configure_paned_window(self):
        """Configure the paned window settings"""
        # Set initial sash position (approximately 2/3 for content, 1/3 for logs)
        # This will be calculated based on the window width
        self.root.after(100, self._set_initial_sash_position)
    
    def _set_initial_sash_position(self):
        """Set the initial sash position after the window is fully rendered"""
        try:
            # Get the current width of the paned window
            paned_width = self.paned_window.winfo_width()
            if paned_width <= 100:
                self.root.after(100, self._set_initial_sash_position)
                return
            if len(self.paned_window.panes()) > 1:
                # Keep logs secondary, and make the collapsed panel genuinely compact.
                initial_position = int(paned_width * 0.70)
                self.paned_window.sashpos(0, initial_position)
        except tk.TclError:
            # If there's an error, try again later
            self.root.after(100, self._set_initial_sash_position)
    
    def setup_pages(self):
        """Setup all application pages"""
        self.pages = {}
        
        # Create page instances
        self.media_organizer_page = MediaOrganizerPage(self.content_area, self.log_manager.log_message)
        self.media_converter_page = MediaConverterPage(
            self.content_area,
            self.log_manager.log_message,
            dependency_warnings=self.dependency_warnings,
        )
        
        # Create pages
        self.pages['media_organizer'] = self.media_organizer_page.create_page()
        self.pages['media_converter'] = self.media_converter_page.create_page()
        
        # Update navigation manager with pages
        self.nav_manager.pages = self.pages
        
        # Show the first page by default
        self.nav_manager.show_page('media_organizer')
    
    
    def setup_event_handlers(self):
        """Setup event handlers"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def on_closing(self):
        """Handle window closing"""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.destroy()
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()


def main():
    """Main entry point"""
    app = MediaConverterOrganizerGUI()
    app.run()


if __name__ == "__main__":
    main()
