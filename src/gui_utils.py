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
from pathlib import Path
from PIL import Image
import ctypes
import platform


class WindowManager:
    """Manages window properties and styling"""
    
    @staticmethod
    def set_window_icon(root):
        """Set the window icon from LogoIcon.png"""
        try:
            # Get project root directory (parent of src)
            project_root = Path(__file__).parent.parent
            ico_path = project_root / 'assets' / 'LogoIcon.ico'
            png_path = project_root / 'assets' / 'LogoIcon.png'
            
            # Convert PNG to ICO if needed
            if not ico_path.exists():
                if png_path.exists():
                    img = Image.open(str(png_path))
                    # Create ICO with multiple sizes
                    sizes = [(16, 16), (32, 32), (48, 48), (64, 64)]
                    img.save(str(ico_path), format='ICO', sizes=sizes)
            
            # Set window icon
            if ico_path.exists():
                root.iconbitmap(str(ico_path))
                
                # Set Windows taskbar icon
                if sys.platform == "win32":
                    try:
                        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("MediaConverterOrganizer.1.0")
                    except:
                        pass
            else:
                # Fallback to PNG
                if png_path.exists():
                    root.iconphoto(True, tk.PhotoImage(file=str(png_path)))
                    
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
        """Setup ttk styles for Windows 11 native look"""
        style = ttk.Style()
        
        # Detect Windows 11 and use appropriate theme
        system = platform.system()
        is_windows_11 = False
        if system == "Windows":
            try:
                # Check Windows version
                version = platform.version()
                # Windows 11 is version 10.0.22000 or higher
                major, minor = map(int, version.split('.')[:2])
                if major == 10 and minor >= 22000:
                    is_windows_11 = True
            except:
                pass
        
        # Set theme - prefer 'vista' or 'winnative' for Windows 11 look
        available_themes = style.theme_names()
        if is_windows_11 and 'vista' in available_themes:
            style.theme_use('vista')
        elif 'vista' in available_themes:
            style.theme_use('vista')
        elif 'clam' in available_themes:
            style.theme_use('clam')
        elif 'alt' in available_themes:
            style.theme_use('alt')
        else:
            style.theme_use('default')
        
        # Windows 11 Fluent Design color palette
        colors = {
            # Windows 11 Dark Theme colors (official palette)
            'bg_color': '#202020',           # Windows 11 dark background
            'sidebar_bg': '#1C1C1C',         # Slightly darker sidebar
            'card_bg': '#2D2D2D',            # Card background (lighter than main bg)
            'accent_color': '#0078D4',       # Windows 11 system accent blue
            'accent_hover': '#106EBE',       # Darker blue on hover
            'accent_pressed': '#005A9E',     # Pressed state
            'text_color': '#FFFFFF',         # White text for high contrast
            'muted_text': '#C0C0C0',         # Muted text (light gray)
            'border_color': '#3D3D3D',       # Subtle borders
            'border_hover': '#505050',       # Border on hover
            'success_color': '#107C10',      # Windows 11 success green
            'success_hover': '#0E6B0E',      # Darker green on hover
            'secondary_accent': '#00BCF2',   # Secondary accent (cyan)
            'warning_color': '#FFB900',      # Windows 11 warning amber
            'error_color': '#D13438',        # Windows 11 error red
            'info_color': '#0078D4',         # Info blue (same as accent)
            'hover_bg': '#2D2D2D',           # Hover background (same as card)
            'selected_bg': '#2D2D2D',        # Selected item background (card color)
            'input_bg': '#2D2D2D',           # Input field background
            'input_border': '#3D3D3D',       # Input border
            'input_focus': '#0078D4',        # Input focus border (accent blue)
            'log_bg': '#1C1C1C',            # Log background (darker)
            'log_text': '#FFFFFF',          # White text for logs
        }
        
        # Windows 11 font - try Segoe UI Variable, fallback to Segoe UI
        try:
            # Try Segoe UI Variable (Windows 11 font)
            test_font = ('Segoe UI Variable', 10)
            # If it fails, tkinter will use fallback
        except:
            pass
        
        segoe_font = 'Segoe UI'  # Standard Segoe UI (works on all Windows versions)
        
        # Override default colors
        style.configure('.', background=colors['card_bg'], foreground=colors['text_color'])
        
        # Configure frame styles with dark theme look
        style.configure('Sidebar.TFrame', background=colors['sidebar_bg'])
        style.configure('Content.TFrame', background=colors['bg_color'])
        style.configure('Card.TFrame', background=colors['card_bg'], relief='flat')
        
        # Label styles - Windows 11 typography
        style.configure('Title.TLabel', 
                       font=(segoe_font, 20, 'bold'), 
                       foreground=colors['text_color'], 
                       background=colors['bg_color'])
        style.configure('Subtitle.TLabel',
                       font=(segoe_font, 14, 'normal'),
                       foreground=colors['muted_text'],
                       background=colors['bg_color'])
        style.configure('Info.TLabel', 
                       font=(segoe_font, 10, 'normal'), 
                       foreground=colors['text_color'], 
                       background=colors['card_bg'])
        style.configure('Section.TLabel',
                       font=(segoe_font, 13, 'bold'),
                       foreground=colors['text_color'],
                       background=colors['card_bg'])
        style.configure('SectionHeader.TLabel',
                       font=(segoe_font, 13, 'bold'),
                       foreground=colors['text_color'],
                       background=colors['card_bg'],
                       padding=(0, 0, 0, 8))
        style.configure('Success.TLabel',
                       font=(segoe_font, 9, 'normal'),
                       foreground=colors['success_color'],
                       background=colors['bg_color'])
        
        # Button styles - Gray buttons with white text
        style.configure('Nav.TButton', 
                       font=(segoe_font, 11, 'normal'), 
                       padding=(16, 10),
                       relief='flat',
                       borderwidth=0,
                       focuscolor='none')
        style.configure('Primary.TButton',
                       font=(segoe_font, 10, 'normal'),
                       padding=(16, 8),
                       relief='flat',
                       borderwidth=0,
                       background='#4A4A4A',  # Gray background
                       foreground='#FFFFFF')  # White text
        style.configure('Success.TButton',
                       font=(segoe_font, 10, 'normal'),
                       padding=(16, 8),
                       relief='flat',
                       borderwidth=0,
                       background='#4A4A4A',  # Gray background
                       foreground='#FFFFFF')  # White text
        style.configure('Danger.TButton',
                       font=(segoe_font, 10, 'normal'),
                       padding=(16, 8),
                       relief='flat',
                       borderwidth=0,
                       background='#4A4A4A',  # Gray background
                       foreground='#FFFFFF')  # White text
        style.configure('Secondary.TButton',
                       font=(segoe_font, 10, 'normal'),
                       padding=(16, 8),
                       relief='flat',
                       borderwidth=1)
        
        # Entry and combobox styles - Light input fields with dark text for readability
        style.configure('TEntry',
                       font=(segoe_font, 10),
                       padding=(8, 6),
                       fieldbackground='#FFFFFF',  # White background
                       foreground='#000000',  # Black text
                       borderwidth=1,
                       relief='solid',
                       bordercolor=colors['input_border'])
        style.configure('TCombobox',
                       font=(segoe_font, 10),
                       padding=(8, 6),
                       fieldbackground='#FFFFFF',  # White background
                       foreground='#000000',  # Black text
                       borderwidth=1,
                       relief='solid')
        
        # LabelFrame styles - Dark theme (borders removed)
        style.configure('TLabelframe', background=colors['card_bg'], borderwidth=0, relief='flat')
        style.configure('TLabelframe.Label', 
                       font=(segoe_font, 11, 'bold'), 
                       foreground=colors['text_color'], 
                       background=colors['card_bg'])
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
        
        # Scrollbar styles - Windows 11 dark theme scrollbars
        style.configure('TScrollbar',
                       background=colors['border_color'],
                       troughcolor=colors['bg_color'],
                       borderwidth=0,
                       arrowcolor=colors['muted_text'],
                       darkcolor=colors['border_color'],
                       lightcolor=colors['border_color'])
        style.map('TScrollbar',
                 background=[('active', colors['accent_color'])],  # Blue accent on hover
                 arrowcolor=[('active', colors['accent_color'])])
        
        # PanedWindow styles - Windows 11 dark theme divider
        style.configure('TPanedwindow', background=colors['bg_color'])
        style.configure('TPanedwindow.Sash',
                       background=colors['border_color'],
                       relief='flat',
                       width=1)
        style.map('TPanedwindow.Sash',
                 background=[('hover', colors['accent_color'])])  # Blue accent on hover
        
        # Frame styles
        style.configure('TFrame', background=colors['card_bg'])
        
        # Default TLabel style - inherits from parent frame
        style.configure('TLabel',
                       background=colors['card_bg'],
                       foreground=colors['text_color'],
                       font=(segoe_font, 10))
        
        # Map button states - Windows 11 hover effects
        style.map('Nav.TButton',
                 background=[('active', colors['hover_bg']),
                           ('pressed', colors['selected_bg'])],
                 foreground=[('active', colors['text_color']),
                           ('pressed', colors['text_color'])],
                 bordercolor=[('focus', colors['accent_color'])])
        
        style.map('Primary.TButton',
                 background=[('active', '#5A5A5A'),  # Lighter gray on hover
                           ('pressed', '#3A3A3A')],  # Darker gray when pressed
                 foreground=[('active', '#E0E0E0'),  # Darker white (light gray) on hover
                           ('pressed', '#FFFFFF'),
                           ('!active', '#FFFFFF'),  # White text when not active
                           ('!disabled', '#FFFFFF')])
        
        style.map('Success.TButton',
                 background=[('active', '#5A5A5A'),  # Lighter gray on hover
                           ('pressed', '#3A3A3A')],  # Darker gray when pressed
                 foreground=[('active', '#E0E0E0'),  # Darker white (light gray) on hover
                           ('pressed', '#FFFFFF'),
                           ('!active', '#FFFFFF'),  # White text when not active
                           ('!disabled', '#FFFFFF'),
                           ('disabled', '#666666')])
        
        style.map('Danger.TButton',
                 background=[('active', '#5A5A5A'),  # Lighter gray on hover
                           ('pressed', '#3A3A3A')],  # Darker gray when pressed
                 foreground=[('active', '#E0E0E0'),  # Darker white (light gray) on hover
                           ('pressed', '#FFFFFF'),
                           ('!active', '#FFFFFF'),  # White text when not active
                           ('!disabled', '#FFFFFF')])
        
        style.map('Secondary.TButton',
                 background=[('active', colors['hover_bg']),
                           ('pressed', colors['border_color'])],
                 bordercolor=[('active', colors['border_hover']),
                            ('pressed', colors['border_hover'])])
        
        # Entry focus effects - Blue accent border on focus
        style.map('TEntry',
                 fieldbackground=[('focus', '#FFFFFF')],  # Keep white background on focus
                 bordercolor=[('focus', colors['input_focus'])],  # Blue accent on focus
                 lightcolor=[('focus', colors['input_focus'])],
                 darkcolor=[('focus', colors['input_focus'])],
                 foreground=[('focus', '#000000')])  # Keep black text on focus
        
        style.map('TCombobox',
                 fieldbackground=[('readonly', '#FFFFFF'),
                                ('active', '#FFFFFF')],  # White background
                 bordercolor=[('focus', colors['input_focus'])],  # Blue accent on focus
                 arrowcolor=[('active', colors['accent_color']),  # Blue arrow
                           ('!active', colors['muted_text'])],
                 foreground=[('focus', '#000000'),  # Black text
                           ('readonly', '#000000'),
                           ('active', '#000000')])
        
        return style
    
    @staticmethod
    def create_gray_button(parent, text, command=None, state=tk.NORMAL, **kwargs):
        """Create a gray button with white text and hover effects"""
        # Set disabled colors
        disabled_bg = '#3A3A3A'
        disabled_fg = '#666666'
        
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            state=state,
            font=('Segoe UI', 10, 'normal'),
            bg='#4A4A4A' if state == tk.NORMAL else disabled_bg,  # Gray background
            fg='#FFFFFF' if state == tk.NORMAL else disabled_fg,  # White text
            activebackground='#3A3A3A',  # Darker gray when pressed
            activeforeground='#FFFFFF',
            disabledforeground=disabled_fg,
            relief='flat',
            borderwidth=0,
            padx=16,
            pady=8,
            cursor='hand2',
            **kwargs
        )
        # Add hover effect - lighter gray with darker white text
        def on_enter(e):
            if btn['state'] != 'disabled':
                btn.config(bg='#5A5A5A', fg='#E0E0E0')
        def on_leave(e):
            if btn['state'] != 'disabled':
                btn.config(bg='#4A4A4A', fg='#FFFFFF')
            else:
                btn.config(bg=disabled_bg, fg=disabled_fg)
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)
        
        # Override configure to handle state changes
        original_configure = btn.configure
        def configure_wrapper(**kw):
            result = original_configure(**kw)
            if 'state' in kw:
                new_state = kw['state']
                if new_state == tk.DISABLED:
                    btn.config(bg=disabled_bg, fg=disabled_fg)
                else:
                    btn.config(bg='#4A4A4A', fg='#FFFFFF')
            return result
        btn.configure = configure_wrapper
        return btn
    
    @staticmethod
    def create_modern_section(parent, title, padding=20):
        """
        Create a modern Windows 11 dark theme section with header and separator.
        Returns: (section_frame, content_frame)
        """
        # Windows 11 dark theme colors
        card_bg = '#2D2D2D'  # Card background (lighter than main bg)
        text_color = '#FFFFFF'  # White text
        border_color = '#3D3D3D'  # Border color
        
        # Main section frame with Windows 11 dark card background
        section_frame = tk.Frame(parent, bg=card_bg, relief='flat')
        
        # Header frame
        header_frame = tk.Frame(section_frame, bg=card_bg)
        header_frame.pack(fill=tk.X, pady=(0, 16), padx=padding, anchor=tk.W)
        
        # Section title
        title_label = tk.Label(header_frame,
                              text=title,
                              font=('Segoe UI', 13, 'bold'),
                              bg=card_bg,
                              fg=text_color,
                              anchor='w')
        title_label.pack(side=tk.LEFT)
        
        # Subtle separator line
        separator = tk.Frame(section_frame, bg=border_color, height=1)
        separator.pack(fill=tk.X, padx=padding, pady=(0, padding))
        
        # Content frame with padding
        content_frame = tk.Frame(section_frame, bg=card_bg)
        content_frame.pack(fill=tk.X, padx=padding, pady=(0, padding))
        
        return section_frame, content_frame
    
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
        # Windows 11 dark theme color scheme for logs
        self.color_map = {
            "INFO": "#FFFFFF",        # White for info
            "SUCCESS": "#107C10",     # Windows 11 success green
            "WARNING": "#FFB900",     # Windows 11 warning amber
            "ERROR": "#D13438"        # Windows 11 error red
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
                    # Insert message with newline
                    self.log_widget.insert(tk.END, message + "\n")
                    
                    # Color the last line based on log level
                    start_line = self.log_widget.index(tk.END + "-2l")
                    end_line = self.log_widget.index(tk.END + "-1l")
                    
                    # Configure tag for this log level
                    tag_name = f"log_{level}"
                    self.log_widget.tag_add(tag_name, start_line, end_line)
                    self.log_widget.tag_config(
                        tag_name,
                        foreground=self.color_map.get(level, "#202020"),
                        font=('Consolas', 9)
                    )
                    
                    # Auto-scroll to bottom
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
        """Create the sidebar navigation with Windows 11 dark theme styling"""
        # Windows 11 dark theme colors
        sidebar_bg = '#1C1C1C'  # Windows 11 dark sidebar
        text_color = '#FFFFFF'  # White text
        hover_bg = '#2D2D2D'    # Hover background (card color)
        selected_bg = '#2D2D2D' # Selected background
        
        sidebar = tk.Frame(self.parent, bg=sidebar_bg, width=260)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        
        # App title and logo with Windows 11 spacing
        title_frame = tk.Frame(sidebar, bg=sidebar_bg)
        title_frame.pack(fill=tk.X, padx=16, pady=(24, 24))
        
        try:
            # Get project root directory
            project_root = Path(__file__).parent.parent
            logo_path = project_root / 'assets' / 'LogoIcon.png'
            if logo_path.exists():
                logo_image = tk.PhotoImage(file=str(logo_path))
                logo_image = logo_image.subsample(6, 6)  # Make it smaller
                logo_label = tk.Label(title_frame, image=logo_image, bg=sidebar_bg)
                logo_label.image = logo_image  # Keep a reference
                logo_label.pack(pady=(0, 12))
            else:
                raise FileNotFoundError("Logo not found")
        except:
            # Fallback to text
            logo_label = tk.Label(title_frame, text="🎮", 
                                font=('Segoe UI', 28), 
                                bg=sidebar_bg, 
                                fg=text_color)
            logo_label.pack(pady=(0, 12))
        
        app_title = tk.Label(title_frame, 
                            text="Media Converter\n& Organizer", 
                            font=('Segoe UI', 15, 'bold'), 
                            bg=sidebar_bg, 
                            fg=text_color, 
                            justify=tk.CENTER)
        app_title.pack()
        
        # Navigation buttons with Windows 11 style
        nav_frame = tk.Frame(sidebar, bg=sidebar_bg)
        nav_frame.pack(fill=tk.X, padx=8, pady=(8, 0))
        
        # Navigation items
        nav_items = [
            ("📁 Media Organizer", "media_organizer"),
            ("🔄 Media Converter", "media_converter")
        ]
        
        for text, page_id in nav_items:
            # Create button frame for rounded corners effect
            btn_frame = tk.Frame(nav_frame, bg=sidebar_bg)
            btn_frame.pack(fill=tk.X, pady=(0, 4))
            
            btn = tk.Button(btn_frame, 
                           text=text, 
                           command=lambda p=page_id: self.show_page(p), 
                           bg=sidebar_bg,
                           fg=text_color,
                           font=('Segoe UI', 11, 'normal'),
                           relief='flat',
                           bd=0,
                           padx=12,
                           pady=10,
                           anchor='w',
                           activebackground=hover_bg,
                           activeforeground=text_color,
                           cursor='hand2')
            btn.pack(fill=tk.X)
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
        
        # Update navigation button styles - Windows 11 dark theme active state
        sidebar_bg = '#1C1C1C'  # Windows 11 dark sidebar
        text_color = '#FFFFFF'  # White text
        selected_bg = '#2D2D2D' # Selected background (card color)
        accent_color = '#0078D4'  # Windows 11 accent blue
        
        for btn_id, btn in self.nav_buttons.items():
            if btn_id == page_id:
                # Active state - Windows 11 style with card background
                btn.configure(bg=selected_bg, 
                            fg=text_color,  # White text for active
                            font=('Segoe UI', 11, 'bold'))
            else:
                # Normal state
                btn.configure(bg=sidebar_bg, 
                            fg=text_color,
                            font=('Segoe UI', 11, 'normal'))
