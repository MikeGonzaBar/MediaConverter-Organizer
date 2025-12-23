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
        
        # Create a paned window for resizable content and logs panels
        # Users can drag the sash (divider) to resize the Activity Log panel
        self.paned_window = ttk.PanedWindow(self.main_container, orient=tk.HORIZONTAL)
        self.paned_window.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Content area (left side of paned window)
        self.content_area = ttk.Frame(self.paned_window, style='Content.TFrame')
        self.paned_window.add(self.content_area, weight=2)  # Give it more weight initially
        
        # Persistent logs panel on the right (resizable) - Windows 11 dark theme
        self.logs_panel = tk.Frame(self.paned_window, bg='#1C1C1C')  # Windows 11 dark background
        self.paned_window.add(self.logs_panel, weight=1)  # Give it less weight initially
        
        # Configure the paned window after adding all panes
        self.configure_paned_window()
        
        # Logs header with title and clear button
        logs_header = tk.Frame(self.logs_panel, bg='#1C1C1C')
        logs_header.pack(fill=tk.X, padx=20, pady=(16, 0))
        
        logs_title = tk.Label(
            logs_header, 
            text="📝 Activity Logs",
            font=('Segoe UI', 13, 'bold'),
            bg='#1C1C1C',
            fg='#FFFFFF',
            anchor='w'
        )
        logs_title.pack(side=tk.LEFT)
        
        # Clear logs button - Gray button style
        clear_logs_btn = tk.Button(
            logs_header,
            text="🗑️ Clear",
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
        
        # Subtle separator line
        logs_separator = tk.Frame(self.logs_panel, bg='#3D3D3D', height=1)
        logs_separator.pack(fill=tk.X, padx=20, pady=(12, 12))
        
        # Log display widget - Windows 11 dark theme
        from tkinter import scrolledtext
        self.side_log_text = scrolledtext.ScrolledText(
            self.logs_panel,
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
            self.side_log_text.delete(1.0, tk.END)
            self.log_manager.log_message("Logs cleared", "INFO")
    
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
            if paned_width > 100:  # Make sure the window is rendered
                # Set sash to approximately 2/3 of the width
                initial_position = int(paned_width * 0.67)
                self.paned_window.sash_place(0, initial_position, 0)
        except tk.TclError:
            # If there's an error, try again later
            self.root.after(100, self._set_initial_sash_position)
    
    def setup_pages(self):
        """Setup all application pages"""
        self.pages = {}
        
        # Create page instances
        self.media_organizer_page = MediaOrganizerPage(self.content_area, self.log_manager.log_message)
        self.media_converter_page = MediaConverterPage(self.content_area, self.log_manager.log_message)
        
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
