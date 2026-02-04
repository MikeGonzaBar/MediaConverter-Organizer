"""
GUI Utilities Module
Contains common GUI utilities and styling functions
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
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
    def setup_styles(theme_manager):
        """Setup ttkbootstrap styles"""
        style = theme_manager.style
        
        # Configure common styles using bootstrap conventions
        style.configure('TFrame', padding=10)
        style.configure('Sidebar.TFrame', padding=10)
        style.configure('Content.TFrame', padding=20)
        style.configure('Card.TFrame', padding=15, relief='flat')
        
        style.configure('Title.TLabel', font=('Helvetica', 20, 'bold'), padding=10)
        style.configure('Subtitle.TLabel', font=('Helvetica', 14), padding=5)
        style.configure('Info.TLabel', font=('Helvetica', 10), padding=5)
        style.configure('Section.TLabel', font=('Helvetica', 13, 'bold'), padding=5)
        style.configure('SectionHeader.TLabel', font=('Helvetica', 13, 'bold'), padding=(0, 0, 0, 8))
        style.configure('Success.TLabel', font=('Helvetica', 9), padding=5)
        
        style.configure('Nav.TButton', font=('Helvetica', 11), padding=(16, 10), anchor='w')
        style.configure('Primary.TButton', font=('Helvetica', 10), padding=(16, 8))
        style.configure('Success.TButton', font=('Helvetica', 10), padding=(16, 8))
        style.configure('Danger.TButton', font=('Helvetica', 10), padding=(16, 8))
        style.configure('Secondary.TButton', font=('Helvetica', 10), padding=(16, 8))
        
        style.configure('TEntry', font=('Helvetica', 10), padding=(8, 6))
        style.configure('TCombobox', font=('Helvetica', 10), padding=(8, 6))
        
        style.configure('TLabelframe', relief='flat', padding=10)
        style.configure('TLabelframe.Label', font=('Helvetica', 11, 'bold'))
        
        return style
    
    @staticmethod
    def create_gray_button(parent, text, command=None, state=tk.NORMAL, **kwargs):
        """Create a themed button using ttkbootstrap"""
        btn = ttkb.Button(
            parent,
            text=text,
            command=command,
            state=state,
            bootstyle=SECONDARY,
            padding=(16, 8),
            **kwargs
        )
        return btn
    
    @staticmethod
    def create_modern_section(parent, title, padding=20, theme_manager=None):
        """
        Create a modern theme-aware section with header and separator.
        Returns: (section_frame, content_frame)
        """
        if theme_manager is None:
            raise ValueError("ThemeManager is required for create_modern_section")
            
        colors = theme_manager.style.colors
        
        # Use theme-aware colors
        card_bg = colors.inputbg  # Subtle background for sections
        text_color = colors.fg
        border_color = colors.border
        
        # Main section frame with theme background
        section_frame = ttk.Frame(parent, style='Card.TFrame')
        
        # Header frame
        header_frame = ttk.Frame(section_frame)
        header_frame.pack(fill=tk.X, pady=(0, 16), padx=padding, anchor=tk.W)
        
        # Section title using configured style
        title_label = ttk.Label(header_frame,
                              text=title,
                              style='Section.TLabel',
                              anchor='w')
        title_label.pack(side=tk.LEFT)
        
        # Subtle separator
        separator = ttk.Separator(section_frame, orient='horizontal')
        separator.pack(fill=tk.X, padx=padding, pady=(0, padding))
        
        # Content frame
        content_frame = ttk.Frame(section_frame)
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
    
    def __init__(self, log_widget=None, theme_manager=None):
        self.log_widget = log_widget
        self.theme_manager = theme_manager
        self.log_queue = queue.Queue()
        self.update_color_map()
    
    def update_color_map(self):
        """Update color map based on current theme"""
        if self.theme_manager:
            colors = self.theme_manager.style.colors
            self.color_map = {
                "INFO": colors.inputfg,
                "SUCCESS": colors.success,
                "WARNING": colors.warning,
                "ERROR": colors.danger
            }
        else:
            # Default colors if no theme manager
            self.color_map = {
                "INFO": "#FFFFFF",
                "SUCCESS": "#107C10",
                "WARNING": "#FFB900",
                "ERROR": "#D13438"
            }
        # Reconfigure existing tags if widget exists
        if self.log_widget:
            for level in self.color_map:
                tag_name = f"log_{level}"
                self.log_widget.tag_config(
                    tag_name,
                    foreground=self.color_map[level],
                    font=('Consolas', 9)
                )
    
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
    
    def __init__(self, parent, content_area, pages, theme_manager):
        self.parent = parent
        self.content_area = content_area
        self.pages = pages
        self.theme_manager = theme_manager
        self.nav_buttons = {}
        self.current_page = None
    
    def create_sidebar(self):
        """Create the sidebar navigation using ttkbootstrap"""
        sidebar = ttkb.Frame(self.parent, bootstyle="dark", width=260)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        
        # App title and logo
        title_frame = ttkb.Frame(sidebar)
        title_frame.pack(fill=tk.X, padx=16, pady=(24, 24))
        
        try:
            project_root = Path(__file__).parent.parent
            logo_path = project_root / 'assets' / 'LogoIcon.png'
            if logo_path.exists():
                logo_image = tk.PhotoImage(file=str(logo_path))
                logo_image = logo_image.subsample(6, 6)
                logo_label = ttkb.Label(title_frame, image=logo_image)
                logo_label.image = logo_image
                logo_label.pack(pady=(0, 12))
            else:
                raise FileNotFoundError("Logo not found")
        except:
            logo_label = ttkb.Label(title_frame, text="🎮", font=('Helvetica', 28))
            logo_label.pack(pady=(0, 12))
        
        app_title = ttkb.Label(title_frame, 
                               text="Media Converter\n& Organizer", 
                               font=('Helvetica', 15, 'bold'),
                               justify=tk.CENTER)
        app_title.pack()
        
        # Navigation buttons
        nav_frame = ttkb.Frame(sidebar)
        nav_frame.pack(fill=tk.X, padx=8, pady=(8, 0))
        
        nav_items = [
            ("📁 Media Organizer", "media_organizer"),
            ("🔄 Media Converter", "media_converter")
        ]
        
        for text, page_id in nav_items:
            btn = ttkb.Button(nav_frame, 
                              text=text, 
                              command=lambda p=page_id: self.show_page(p),
                              bootstyle="secondary-outline-toolbutton",
                              padding=(12, 10))
            btn.pack(fill=tk.X, pady=2)
            self.nav_buttons[page_id] = btn
        
        # Theme toggle button with icons
        icon = "🌙" if self.theme_manager.current_theme in self.theme_manager.light_themes else "☀️"
        self.theme_button = ttkb.Button(nav_frame, 
                                        text=icon,
                                        bootstyle="primary",
                                        command=self.toggle_and_update_button,
                                        width=3)
        self.theme_button.pack(pady=10)
        
        return sidebar
    
    def show_page(self, page_id):
        """Show the specified page and update navigation"""
        for page in self.pages.values():
            page.pack_forget()
        
        if page_id in self.pages:
            self.pages[page_id].pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            self.current_page = page_id
        
        # Update button states with consistent styling
        for btn_id, btn in self.nav_buttons.items():
            if btn_id == page_id:
                btn.configure(bootstyle="primary-outline-toolbutton")
            else:
                btn.configure(bootstyle="secondary-outline-toolbutton")

    def toggle_and_update_button(self):
        """Toggle theme and update button icon"""
        self.theme_manager.toggle_theme()
        icon = "🌙" if self.theme_manager.current_theme in self.theme_manager.light_themes else "☀️"
        self.theme_button.configure(text=icon)
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *

class ThemeManager:
    """Manages theme switching and palette access"""
    
    def __init__(self, root):
        self.root = root
        self.style = ttkb.Style()
        self.current_theme = 'darkly'  # Default to dark
        self.dark_themes = ['darkly', 'cyborg', 'superhero']
        self.light_themes = ['flatly', 'litera', 'cosmo']
        self.non_ttk_widgets = []  # List to track widgets needing manual refresh
        self.apply_theme(self.current_theme)

    def configure_custom_styles(self):
        """Configure custom styles with theme-aware properties"""
        colors = self.style.colors
        
        # Reconfigure common styles
        self.style.configure('TFrame', padding=10)
        self.style.configure('Sidebar.TFrame', padding=10)
        self.style.configure('Content.TFrame', padding=20)
        self.style.configure('Card.TFrame', background=colors.inputbg, padding=15, relief='flat')
        
        self.style.configure('Title.TLabel', font=('Helvetica', 20, 'bold'), padding=10, foreground=colors.fg)
        self.style.configure('Subtitle.TLabel', font=('Helvetica', 14), padding=5, foreground=colors.fg)
        self.style.configure('Info.TLabel', font=('Helvetica', 10), padding=5, foreground=colors.fg)
        self.style.configure('Section.TLabel', font=('Helvetica', 13, 'bold'), padding=5, foreground=colors.fg)
        self.style.configure('SectionHeader.TLabel', font=('Helvetica', 13, 'bold'), padding=(0, 0, 0, 8), foreground=colors.fg)
        self.style.configure('Success.TLabel', font=('Helvetica', 9), padding=5, foreground=colors.success)
        
        self.style.configure('Nav.TButton', font=('Helvetica', 11), padding=(16, 10), anchor='w')
        self.style.configure('Primary.TButton', font=('Helvetica', 10), padding=(16, 8))
        self.style.configure('Success.TButton', font=('Helvetica', 10), padding=(16, 8))
        self.style.configure('Danger.TButton', font=('Helvetica', 10), padding=(16, 8))
        self.style.configure('Secondary.TButton', font=('Helvetica', 10), padding=(16, 8))
        
        self.style.configure('TEntry', font=('Helvetica', 10), padding=(8, 6))
        self.style.configure('TCombobox', font=('Helvetica', 10), padding=(8, 6))
        
        self.style.configure('TLabelframe', relief='flat', padding=10)
        self.style.configure('TLabelframe.Label', font=('Helvetica', 11, 'bold'), foreground=colors.fg)

    def apply_theme(self, theme_name):
        """Apply the selected theme and update colors"""
        self.style.theme_use(theme_name)
        self.current_theme = theme_name
        self.configure_custom_styles()  # Reconfigure custom styles with new theme colors
        self.root.update_idletasks()  # Force UI update before refresh
        self.refresh_non_ttk_widgets()

    def toggle_theme(self):
        """Toggle between light and dark themes"""
        if self.current_theme in self.dark_themes:
            self.apply_theme('flatly')  # Switch to a light theme
        else:
            self.apply_theme('darkly')  # Switch to a dark theme

    def get_color(self, color_type):
        """Get theme-aware color"""
        colors = self.style.colors
        color_map = {
            'bg': colors.bg,
            'fg': colors.fg,
            'primary': colors.primary,
            'secondary': colors.secondary,
            'success': colors.success,
            'info': colors.info,
            'warning': colors.warning,
            'danger': colors.danger,
            'light': colors.light,
            'dark': colors.dark,
            'input_bg': colors.inputbg,
            'input_fg': colors.inputfg,
            'select_bg': colors.selectbg,
            'select_fg': colors.selectfg,
            'border': colors.border
        }
        return color_map.get(color_type, colors.bg)

    def register_non_ttk_widget(self, widget):
        """Register widgets that need manual theme updates (e.g., Canvas, ScrolledText)"""
        self.non_ttk_widgets.append(widget)
        self.refresh_widget(widget)

    def refresh_non_ttk_widgets(self):
        """Refresh all registered non-ttk widgets with current theme colors"""
        for widget in self.non_ttk_widgets:
            self.refresh_widget(widget)

    def refresh_widget(self, widget):
        """Refresh a single widget's colors based on type"""
        colors = self.style.colors
        if isinstance(widget, tk.Canvas):
            widget.configure(bg=colors.bg, highlightbackground=colors.border)
        elif isinstance(widget, tk.Text) or isinstance(widget, scrolledtext.ScrolledText):
            widget.configure(
                bg=colors.inputbg,
                fg=colors.inputfg,
                insertbackground=colors.selectfg,
                selectbackground=colors.selectbg,
                selectforeground=colors.selectfg,
                borderwidth=1,
                highlightthickness=1,
                highlightbackground=colors.border,
                highlightcolor=colors.primary
            )
        elif isinstance(widget, tk.Frame):
            widget.configure(bg=colors.bg)
        elif isinstance(widget, tk.Label):
            widget.configure(bg=colors.bg, fg=colors.fg)
        elif isinstance(widget, tk.Button):
            widget.configure(
                bg=colors.secondary,
                fg=colors.fg,
                activebackground=colors.primary,
                activeforeground=colors.selectfg
            )
        # Add more widget types as needed

