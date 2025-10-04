"""
GUI Utilities Module
Contains common GUI utilities and styling functions
"""

import tkinter as tk
from tkinter import ttk
import os
import sys
import queue
from datetime import datetime
from PIL import Image
import ctypes


class WindowManager:
    """Manages window properties and styling"""
    
    @staticmethod
    def set_window_icon(root):
        """Set the window icon from LogoIcon.png"""
        try:
            # Convert PNG to ICO if needed
            if not os.path.exists('LogoIcon.ico'):
                if os.path.exists('LogoIcon.png'):
                    img = Image.open('LogoIcon.png')
                    # Create ICO with multiple sizes
                    sizes = [(16, 16), (32, 32), (48, 48), (64, 64)]
                    img.save('LogoIcon.ico', format='ICO', sizes=sizes)
            
            # Set window icon
            if os.path.exists('LogoIcon.ico'):
                root.iconbitmap('LogoIcon.ico')
                
                # Set Windows taskbar icon
                if sys.platform == "win32":
                    try:
                        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("MediaConverterOrganizer.1.0")
                    except:
                        pass
            else:
                # Fallback to PNG
                if os.path.exists('LogoIcon.png'):
                    root.iconphoto(True, tk.PhotoImage(file='LogoIcon.png'))
                    
        except Exception as e:
            print(f"Warning: Could not set window icon: {e}")
    
    @staticmethod
    def center_window(root, width=1000, height=750):
        """Center the window on the screen"""
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        root.geometry(f"{width}x{height}+{x}+{y}")
    
    @staticmethod
    def setup_styles():
        """Setup ttk styles for the application"""
        style = ttk.Style()
        
        # Set theme - try different themes for compatibility
        available_themes = style.theme_names()
        if 'clam' in available_themes:
            style.theme_use('clam')
        elif 'vista' in available_themes:
            style.theme_use('vista')
        elif 'alt' in available_themes:
            style.theme_use('alt')
        else:
            style.theme_use('default')
        
        # Define colors matching LogoIcon.png
        colors = {
            'bg_color': '#f8f9fa',
            'sidebar_bg': '#e9ecef', 
            'card_bg': '#ffffff',
            'accent_color': '#20b2aa',
            'text_color': '#212529',
            'muted_text': '#6c757d',
            'border_color': '#dee2e6',
            'success_color': '#28a745',
            'warning_color': '#ffc107',
            'error_color': '#dc3545',
            'info_color': '#17a2b8'
        }
        
        # Override default colors to prevent gray areas
        style.configure('.', background=colors['card_bg'], foreground=colors['text_color'])
        
        # Configure styles
        style.configure('Sidebar.TFrame', background=colors['sidebar_bg'])
        style.configure('Content.TFrame', background=colors['bg_color'])
        style.configure('Title.TLabel', font=('Segoe UI', 24, 'bold'), foreground=colors['text_color'], background=colors['bg_color'])
        style.configure('Info.TLabel', font=('Segoe UI', 10, 'bold'), foreground=colors['text_color'], background=colors['card_bg'])
        
        # Button styles
        style.configure('Nav.TButton', font=('Segoe UI', 11), padding=(20, 10))
        style.configure('Primary.TButton', font=('Segoe UI', 10), padding=(10, 5))
        style.configure('Success.TButton', font=('Segoe UI', 10), padding=(10, 5))
        style.configure('Danger.TButton', font=('Segoe UI', 10), padding=(10, 5))
        
        # Entry and combobox styles
        style.configure('TEntry', font=('Segoe UI', 10), padding=5)
        style.configure('TCombobox', font=('Segoe UI', 10), padding=5)
        
        # LabelFrame styles - completely remove borders
        style.configure('TLabelframe', background=colors['card_bg'], borderwidth=0, relief='flat')
        style.configure('TLabelframe.Label', font=('Segoe UI', 11, 'bold'), foreground=colors['text_color'], background=colors['card_bg'])
        style.configure('TLabelframe.Border', background=colors['card_bg'], borderwidth=0)
        
        # Force all LabelFrame states to have no borders
        style.map('TLabelframe',
                 background=[('active', colors['card_bg']),
                           ('pressed', colors['card_bg']),
                           ('focus', colors['card_bg'])],
                 borderwidth=[('active', 0),
                            ('pressed', 0),
                            ('focus', 0)],
                 relief=[('active', 'flat'),
                        ('pressed', 'flat'),
                        ('focus', 'flat')])
        
        # Also map the border element
        style.map('TLabelframe.Border',
                 background=[('active', colors['card_bg']),
                           ('pressed', colors['card_bg']),
                           ('focus', colors['card_bg'])],
                 borderwidth=[('active', 0),
                            ('pressed', 0),
                            ('focus', 0)])
        
        # Scrollbar styles
        style.configure('TScrollbar', background=colors['border_color'])
        
        # PanedWindow styles
        style.configure('TPanedwindow', background=colors['bg_color'])
        style.configure('TPanedwindow.Sash', background=colors['border_color'], relief='flat')
        
        # Radiobutton and Checkbutton styles
        style.configure('TRadiobutton', background=colors['card_bg'], foreground=colors['text_color'])
        style.configure('TCheckbutton', background=colors['card_bg'], foreground=colors['text_color'])
        
        # Frame styles
        style.configure('TFrame', background=colors['card_bg'])
        style.configure('Content.TFrame', background=colors['bg_color'])
        style.configure('Sidebar.TFrame', background=colors['sidebar_bg'])
        
        # Label styles
        style.configure('TLabel', background=colors['card_bg'], foreground=colors['text_color'])
        style.configure('Title.TLabel', background=colors['bg_color'], foreground=colors['text_color'])
        style.configure('Info.TLabel', background=colors['card_bg'], foreground=colors['text_color'])
        
        # Combobox styles
        style.configure('TCombobox', background='white', foreground=colors['text_color'], fieldbackground='white')
        
        # Remove hover effects that cause gray text
        style.map('TRadiobutton',
                 background=[('active', colors['card_bg']),
                           ('pressed', colors['card_bg']),
                           ('selected', colors['card_bg'])],
                 foreground=[('active', colors['text_color']),
                           ('pressed', colors['text_color']),
                           ('selected', colors['text_color'])])
        
        style.map('TCheckbutton',
                 background=[('active', colors['card_bg']),
                           ('pressed', colors['card_bg']),
                           ('selected', colors['card_bg'])],
                 foreground=[('active', colors['text_color']),
                           ('pressed', colors['text_color']),
                           ('selected', colors['text_color'])])
        
        style.map('TCombobox',
                 fieldbackground=[('readonly', 'white'),
                                ('active', 'white')],
                 background=[('readonly', 'white'),
                           ('active', 'white')])
        
        # Map button states
        style.map('Nav.TButton',
                 background=[('active', colors['accent_color']),
                           ('pressed', '#1a9b95')])
        
        style.map('Primary.TButton',
                 background=[('active', colors['accent_color']),
                           ('pressed', '#1a9b95')])
        
        style.map('Success.TButton',
                 background=[('active', colors['success_color']),
                           ('pressed', '#218838')])
        
        style.map('Danger.TButton',
                 background=[('active', colors['error_color']),
                           ('pressed', '#c82333')])
        
        return style
    
    @staticmethod
    def bind_mousewheel(widget, scrollbar):
        """Bind mouse wheel to scrollable widget"""
        def _on_mousewheel(event):
            widget.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            widget.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_from_mousewheel(event):
            widget.unbind_all("<MouseWheel>")
        
        widget.bind('<Enter>', _bind_to_mousewheel)
        widget.bind('<Leave>', _unbind_from_mousewheel)


class LogManager:
    """Manages logging functionality"""
    
    def __init__(self, log_widget=None):
        self.log_widget = log_widget
        self.log_queue = queue.Queue()
        self.color_map = {
            "INFO": "#212529",
            "SUCCESS": "#28a745", 
            "WARNING": "#ffc107",
            "ERROR": "#dc3545"
        }
    
    def log_message(self, message, level="INFO"):
        """Add message to log queue"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {level}: {message}"
        
        self.log_queue.put((formatted_message, level))
    
    def check_queue(self):
        """Check for new log messages and display them"""
        try:
            while True:
                message, level = self.log_queue.get_nowait()
                if self.log_widget:
                    self.log_widget.insert(tk.END, message + "\n")
                    # Color the last line
                    start_line = self.log_widget.index(tk.END + "-2l")
                    end_line = self.log_widget.index(tk.END + "-1l")
                    self.log_widget.tag_add(level, start_line, end_line)
                    self.log_widget.tag_config(level, foreground=self.color_map.get(level, "#212529"))
                    self.log_widget.see(tk.END)
        except queue.Empty:
            pass
        
        # Schedule next check
        if self.log_widget:
            self.log_widget.after(100, self.check_queue)


class NavigationManager:
    """Manages sidebar navigation"""
    
    def __init__(self, parent, content_area, pages):
        self.parent = parent
        self.content_area = content_area
        self.pages = pages
        self.nav_buttons = {}
        self.current_page = None
    
    def create_sidebar(self):
        """Create the sidebar navigation"""
        sidebar = tk.Frame(self.parent, bg='#e9ecef', width=250)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 1))
        sidebar.pack_propagate(False)
        
        # App title and logo
        title_frame = tk.Frame(sidebar, bg='#e9ecef')
        title_frame.pack(fill=tk.X, padx=20, pady=(30, 20))
        
        try:
            logo_image = tk.PhotoImage(file='LogoIcon.png')
            logo_image = logo_image.subsample(6, 6)  # Make it smaller
            logo_label = tk.Label(title_frame, image=logo_image, bg='#e9ecef')
            logo_label.image = logo_image  # Keep a reference
            logo_label.pack(pady=(0, 10))
        except:
            # Fallback to text
            logo_label = tk.Label(title_frame, text="🎮", font=('Segoe UI', 24), bg='#e9ecef', fg='#212529')
            logo_label.pack(pady=(0, 10))
        
        app_title = tk.Label(title_frame, text="Media Converter\n& Organizer", 
                            font=('Segoe UI', 14, 'bold'), bg='#e9ecef', 
                            fg='#212529', justify=tk.CENTER)
        app_title.pack()
        
        # Navigation buttons
        nav_frame = tk.Frame(sidebar, bg='#e9ecef')
        nav_frame.pack(fill=tk.X, padx=20)
        
        # Navigation items
        nav_items = [
            ("📁 Media Organizer", "media_organizer"),
            ("🔄 Media Converter", "media_converter")
        ]
        
        for text, page_id in nav_items:
            btn = tk.Button(nav_frame, text=text, command=lambda p=page_id: self.show_page(p), 
                           bg='#e9ecef', fg='#212529', font=('Segoe UI', 11),
                           relief='flat', bd=0, padx=20, pady=10,
                           activebackground='#20b2aa', activeforeground='white')
            btn.pack(fill=tk.X, pady=(0, 8))
            self.nav_buttons[page_id] = btn
        
        return sidebar
    
    def show_page(self, page_id):
        """Show the specified page and update navigation"""
        # Hide all pages
        for page in self.pages.values():
            page.pack_forget()
        
        # Show selected page
        if page_id in self.pages:
            self.pages[page_id].pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            self.current_page = page_id
        
        # Update navigation button styles
        for btn_id, btn in self.nav_buttons.items():
            if btn_id == page_id:
                btn.configure(bg='#20b2aa', fg='white')  # Active style
            else:
                btn.configure(bg='#e9ecef', fg='#212529')  # Normal style
