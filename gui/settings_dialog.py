import tkinter as tk
from tkinter import ttk, messagebox
from config import get_api_key, set_api_key, get_region, set_region, get_theme, set_theme, get_theme_colors
from status_fetcher import StatusFetcher

class SettingsDialog:
    def __init__(self, parent, theme_callback=None):
        self.parent = parent
        self.theme_callback = theme_callback
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Settings")
        self.dialog.geometry("500x480")
        self.dialog.resizable(False, False)
        
        # Get theme colors
        self.colors = get_theme_colors()
        self.dialog.configure(bg=self.colors['bg_secondary'])
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.status_fetcher = StatusFetcher()
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the settings UI"""
        main_frame = tk.Frame(self.dialog, bg="#2d2d2d")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title = tk.Label(main_frame, text="Settings", 
                        font=("Arial", 14, "bold"), bg="#2d2d2d", fg="white")
        title.pack(pady=(0, 20))
        
        # API Key section
        api_frame = tk.Frame(main_frame, bg="#2d2d2d")
        api_frame.pack(fill=tk.X, pady=(0, 20))
        
        api_label = tk.Label(api_frame, text="Riot API Key:", 
                            font=("Arial", 10, "bold"), bg="#2d2d2d", fg="white")
        api_label.pack(anchor="w", pady=(0, 5))
        
        info_label = tk.Label(api_frame, 
                             text="Get your API key from: https://developer.riotgames.com/",
                             font=("Arial", 8), bg="#2d2d2d", fg="#888888")
        info_label.pack(anchor="w", pady=(0, 8))
        
        self.api_entry = tk.Entry(api_frame, font=("Arial", 10), bg="#1e1e1e", fg="white",
                                 insertbackground="white", relief=tk.FLAT, show="*")
        self.api_entry.pack(fill=tk.X, ipady=5)
        
        # Load current API key
        current_key = get_api_key()
        if current_key:
            self.api_entry.insert(0, current_key)
        
        # Region section
        region_frame = tk.Frame(main_frame, bg="#2d2d2d")
        region_frame.pack(fill=tk.X, pady=(0, 20))
        
        region_label = tk.Label(region_frame, text="Region:", 
                               font=("Arial", 10, "bold"), bg="#2d2d2d", fg="white")
        region_label.pack(anchor="w", pady=(0, 5))
        
        region_info = tk.Label(region_frame, 
                              text="Select your region for server status monitoring",
                              font=("Arial", 8), bg="#2d2d2d", fg="#888888")
        region_info.pack(anchor="w", pady=(0, 8))
        
        # Region dropdown
        self.region_var = tk.StringVar()
        current_region = get_region()
        
        regions = self.status_fetcher.get_all_regions()
        region_names = [f"{name} ({code.upper()})" for code, name in regions]
        
        self.region_combo = ttk.Combobox(region_frame, textvariable=self.region_var,
                                        values=region_names, state="readonly",
                                        font=("Arial", 10))
        self.region_combo.pack(fill=tk.X, ipady=3)
        
        # Set current region
        for idx, (code, name) in enumerate(regions):
            if code == current_region:
                self.region_combo.current(idx)
                break
        
        if not self.region_var.get() and regions:
            self.region_combo.current(0)
        
        # Theme section
        theme_frame = tk.Frame(main_frame, bg="#2d2d2d")
        theme_frame.pack(fill=tk.X, pady=(0, 20))
        
        theme_label = tk.Label(theme_frame, text="Theme:", 
                              font=("Arial", 10, "bold"), bg="#2d2d2d", fg="white")
        theme_label.pack(anchor="w", pady=(0, 5))
        
        theme_info = tk.Label(theme_frame, 
                             text="Choose your preferred color theme (requires restart)",
                             font=("Arial", 8), bg="#2d2d2d", fg="#888888")
        theme_info.pack(anchor="w", pady=(0, 8))
        
        # Theme dropdown
        self.theme_var = tk.StringVar()
        current_theme = get_theme()
        
        themes = [
            ("Dark Grey (Default)", "dark_grey"),
            ("Pure Black", "pure_black"),
            ("Bright/Light", "bright"),
            ("Blue Dark", "blue_dark"),
            ("Purple Dark", "purple_dark")
        ]
        
        theme_names = [name for name, code in themes]
        
        self.theme_combo = ttk.Combobox(theme_frame, textvariable=self.theme_var,
                                       values=theme_names, state="readonly",
                                       font=("Arial", 10))
        self.theme_combo.pack(fill=tk.X, ipady=3)
        
        # Set current theme
        for idx, (name, code) in enumerate(themes):
            if code == current_theme:
                self.theme_combo.current(idx)
                break
        
        if not self.theme_var.get():
            self.theme_combo.current(0)  # Default to first theme
        
        # Buttons
        btn_frame = tk.Frame(main_frame, bg="#2d2d2d")
        btn_frame.pack(pady=(20, 0), fill=tk.X)
        
        save_btn = tk.Button(btn_frame, text="Save", 
                            command=self.save_settings,
                            bg="#0078d4", fg="white", font=("Arial", 11, "bold"),
                            padx=25, pady=10, relief=tk.FLAT, cursor="hand2")
        save_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        cancel_btn = tk.Button(btn_frame, text="Cancel", 
                              command=self.dialog.destroy,
                              bg="#4a4a4a", fg="white", font=("Arial", 11),
                              padx=25, pady=10, relief=tk.FLAT, cursor="hand2")
        cancel_btn.pack(side=tk.LEFT)
    
    def save_settings(self):
        """Save settings"""
        api_key = self.api_entry.get().strip()
        region_selection = self.region_var.get()
        theme_selection = self.theme_var.get()
        
        # Extract region code from selection (format: "EUW (EUW1)")
        if region_selection and '(' in region_selection:
            region_code = region_selection.split('(')[1].rstrip(')').lower()
        else:
            region_code = 'euw1'
        
        # Extract theme code from selection
        themes = [
            ("Dark Grey (Default)", "dark_grey"),
            ("Pure Black", "pure_black"),
            ("Bright/Light", "bright"),
            ("Blue Dark", "blue_dark"),
            ("Purple Dark", "purple_dark")
        ]
        
        theme_code = "dark_grey"  # default
        for name, code in themes:
            if name == theme_selection:
                theme_code = code
                break
        
        success = True
        if api_key:
            success = success and set_api_key(api_key)
        
        success = success and set_region(region_code)
        
        # Check if theme changed before saving
        current_theme = get_theme()
        theme_changed = theme_code != current_theme
        
        success = success and set_theme(theme_code)
        
        if success:
            # Apply theme immediately if changed
            if theme_changed and self.theme_callback:
                self.theme_callback()
            
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", "Failed to save settings")
