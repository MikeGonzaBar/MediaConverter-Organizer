"""
Media Converter & Organizer GUI - Refactored Version
Main application file with modular architecture
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from datetime import datetime
import queue
import threading

# Import our custom modules
from gui_utils import WindowManager, LogManager, NavigationManager
from ui_components import MediaOrganizerPage
from media_converter_page import MediaConverterPage


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
        """Setup main window properties"""
        self.root.title("Media Converter & Organizer")
        # Widen the window to accommodate a right-side logs panel
        WindowManager.center_window(self.root, width=1400, height=800)
        self.root.minsize(1200, 700)
        WindowManager.set_window_icon(self.root)
    
    def setup_styles(self):
        """Setup application styles"""
        self.style = WindowManager.setup_styles()
    
    def setup_logging(self):
        """Setup logging system"""
        self.log_manager = LogManager()
    
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
        
        # Persistent logs panel on the right (resizable)
        self.logs_panel = ttk.Frame(self.paned_window, style='Content.TFrame')
        self.paned_window.add(self.logs_panel, weight=1)  # Give it less weight initially
        
        # Configure the paned window after adding all panes
        self.configure_paned_window()
        
        # Logs title
        logs_title = ttk.Label(self.logs_panel, text="📝 Activity Logs", style='Title.TLabel')
        logs_title.pack(padx=10, pady=(10, 10), anchor=tk.N)
        
        # Log display widget
        from tkinter import scrolledtext
        self.side_log_text = scrolledtext.ScrolledText(
            self.logs_panel,
            wrap=tk.WORD,
            font=('Consolas', 10),
            bg='white',
            fg='#212529',
            insertbackground='#20b2aa',
            selectbackground='#20b2aa'
        )
        self.side_log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Wire the LogManager to the side panel and start queue checking
        self.log_manager.log_widget = self.side_log_text
        self.log_manager.check_queue()
        
        # Update navigation manager with content area
        self.nav_manager.content_area = self.content_area
    
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
