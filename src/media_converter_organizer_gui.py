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
from typing import Any, Dict

# Import our custom modules
from src.gui_utils import WindowManager, LogManager, NavigationManager, ThemeManager
from src.ui_components import MediaOrganizerPage
from src.media_converter_page import MediaConverterPage

# Try to import dependency checker (optional)
# Ensure name is always bound to satisfy type checkers
class _DCPlaceholder:
    def __init__(self) -> None:
        pass
    def check_all(self) -> Dict[str, Any]:
        # Placeholder signature to satisfy type checkers; not used at runtime when checker is unavailable
        return {
            "ffmpeg": False,
            "fpcalc": False,
            "python_packages": ([], [])
        }

DependencyChecker = _DCPlaceholder  # will be replaced if import succeeds
try:
    from src.dependency_checker import DependencyChecker as _RealDependencyChecker
    DependencyChecker = _RealDependencyChecker  # type: ignore[assignment]
    DEPENDENCY_CHECKER_AVAILABLE = True
except ImportError:
    DEPENDENCY_CHECKER_AVAILABLE = False


class MediaConverterOrganizerGUI:
    """Main GUI application class"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.theme_manager = ThemeManager(self.root)
        self.setup_window()
        self.setup_styles()
        self.setup_logging()
        self.pages = {}
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        self.paned_window = ttk.PanedWindow(self.main_container, orient=tk.HORIZONTAL)
        self.paned_window.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.content_area = ttk.Frame(self.paned_window, style='Content.TFrame')
        self.paned_window.add(self.content_area, weight=2)
        self.logs_panel = tk.Frame(self.paned_window, bg=self.theme_manager.get_color('bg'))
        self.paned_window.add(self.logs_panel, weight=1)
        self.configure_paned_window()
        logs_header = tk.Frame(self.logs_panel, bg=self.theme_manager.get_color('bg'))
        logs_header.pack(fill=tk.X, padx=20, pady=(16, 0))
        logs_title = tk.Label(
            logs_header, 
            text="📝 Activity Logs",
            font=('Helvetica', 13, 'bold'),
            bg=self.theme_manager.get_color('bg'),
            fg=self.theme_manager.get_color('fg'),
            anchor='w'
        )
        logs_title.pack(side=tk.LEFT)
        clear_logs_btn = WindowManager.create_gray_button(
            logs_header,
            text="🗑️ Clear",
            command=self.clear_logs
        )
        clear_logs_btn.pack(side=tk.RIGHT)
        logs_separator = tk.Frame(self.logs_panel, bg=self.theme_manager.get_color('border'), height=1)
        logs_separator.pack(fill=tk.X, padx=20, pady=(12, 12))
        self.side_log_text = scrolledtext.ScrolledText(
            self.logs_panel,
            wrap=tk.WORD,
            font=('Consolas', 9),
            borderwidth=1,
            highlightthickness=0,
            relief='solid',
            spacing1=2,
            spacing2=1,
            spacing3=2
        )
        self.side_log_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        self.theme_manager.register_non_ttk_widget(self.side_log_text)
        self.log_manager.log_widget = self.side_log_text
        self.log_manager.check_queue()
        self.setup_pages()
        self.nav_manager = NavigationManager(self.main_container, self.content_area, self.pages, self.theme_manager)
        self.sidebar = self.nav_manager.create_sidebar()
        self.setup_theme_aware_widgets()
        self.setup_event_handlers()
        self.nav_manager.show_page('media_organizer')
    
    def setup_window(self):
        """Setup main window properties"""
        self.root.title("Media Converter & Organizer")
        WindowManager.center_window(self.root, width=1400, height=800)
        self.root.minsize(1200, 700)
        self.root.configure(bg=self.theme_manager.get_color('bg'))
        WindowManager.set_window_icon(self.root)
    
    def setup_styles(self):
        """Setup application styles"""
        self.style = WindowManager.setup_styles(self.theme_manager)
    
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
        
        # Create a paned window for resizable content and logs panels
        self.paned_window = ttk.PanedWindow(self.main_container, orient=tk.HORIZONTAL)
        self.paned_window.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Content area (left side of paned window)
        self.content_area = ttk.Frame(self.paned_window, style='Content.TFrame')
        self.paned_window.add(self.content_area, weight=2)
        
        # Persistent logs panel on the right (resizable)
        self.logs_panel = tk.Frame(self.paned_window, bg=self.theme_manager.get_color('bg'))
        self.paned_window.add(self.logs_panel, weight=1)
        
        # Configure the paned window
        self.configure_paned_window()
        
        # Logs header with title and clear button
        logs_header = tk.Frame(self.logs_panel, bg=self.theme_manager.get_color('bg'))
        logs_header.pack(fill=tk.X, padx=20, pady=(16, 0))
        
        logs_title = tk.Label(
            logs_header, 
            text="📝 Activity Logs",
            font=('Helvetica', 13, 'bold'),
            bg=self.theme_manager.get_color('bg'),
            fg=self.theme_manager.get_color('fg'),
            anchor='w'
        )
        logs_title.pack(side=tk.LEFT)
        
        clear_logs_btn = WindowManager.create_gray_button(
            logs_header,
            text="🗑️ Clear",
            command=self.clear_logs
        )
        clear_logs_btn.pack(side=tk.RIGHT)
        
        # Subtle separator line
        logs_separator = tk.Frame(self.logs_panel, bg=self.theme_manager.get_color('border'), height=1)
        logs_separator.pack(fill=tk.X, padx=20, pady=(12, 12))
        
        # Log display widget
        self.side_log_text = scrolledtext.ScrolledText(
            self.logs_panel,
            wrap=tk.WORD,
            font=('Consolas', 9),
            borderwidth=1,
            highlightthickness=0,
            relief='solid',
            spacing1=2,
            spacing2=1,
            spacing3=2
        )
        self.side_log_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # Register for theme updates
        self.theme_manager.register_non_ttk_widget(self.side_log_text)
        
        # Wire the LogManager to the side panel and start queue checking
        self.log_manager.log_widget = self.side_log_text
        self.log_manager.check_queue()
        
        # Now create navigation manager with content_area defined
        self.nav_manager = NavigationManager(self.main_container, self.content_area, self.pages, self.theme_manager)
        
        # Create sidebar
        self.sidebar = self.nav_manager.create_sidebar()
    
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
        self.media_organizer_page = MediaOrganizerPage(self.content_area, self.log_manager.log_message, self.theme_manager)
        self.media_converter_page = MediaConverterPage(self.content_area, self.log_manager.log_message, self.theme_manager)
        self.pages['media_organizer'] = self.media_organizer_page.create_page()
        self.pages['media_converter'] = self.media_converter_page.create_page()

    def setup_theme_aware_widgets(self):
        """Register non-ttk widgets for theme updates"""
        self.theme_manager.register_non_ttk_widget(self.root)
        self.theme_manager.register_non_ttk_widget(self.main_container)
        self.theme_manager.register_non_ttk_widget(self.content_area)
        self.theme_manager.register_non_ttk_widget(self.logs_panel)
        self.theme_manager.register_non_ttk_widget(self.side_log_text)
        # Add any other tk-based widgets here
    
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
