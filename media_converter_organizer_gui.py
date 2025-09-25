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
        
        # Create a right container that holds the content area and the logs panel
        self.right_container = ttk.Frame(self.main_container, style='Content.TFrame')
        self.right_container.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Content area (left side of right container)
        self.content_area = ttk.Frame(self.right_container, style='Content.TFrame')
        self.content_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Persistent logs panel on the right
        self.logs_panel = ttk.Frame(self.right_container, style='Content.TFrame', width=420)
        self.logs_panel.pack(side=tk.RIGHT, fill=tk.Y)
        self.logs_panel.pack_propagate(False)
        
        # Logs title
        logs_title = ttk.Label(self.logs_panel, text="📝 Activity Logs", style='Title.TLabel')
        logs_title.pack(padx=10, pady=(10, 10), anchor=tk.N)
        
        # Log display widget
        from tkinter import scrolledtext
        self.side_log_text = scrolledtext.ScrolledText(
            self.logs_panel,
            wrap=tk.WORD,
            width=48,
            height=25,
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
