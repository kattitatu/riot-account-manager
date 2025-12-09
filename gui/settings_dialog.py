import tkinter as tk
from tkinter import ttk, messagebox
from config import get_api_key, set_api_key, get_region, set_region
from status_fetcher import StatusFetcher

class SettingsDialog:
    def __init__(self, parent):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Settings")
        self.dialog.geometry("500x350")
        self.dialog.resizable(False, False)
        self.dialog.configure(bg="#2d2d2d")
        
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
        
        # Extract region code from selection (format: "EUW (EUW1)")
        if region_selection and '(' in region_selection:
            region_code = region_selection.split('(')[1].rstrip(')').lower()
        else:
            region_code = 'euw1'
        
        success = True
        if api_key:
            success = success and set_api_key(api_key)
        
        success = success and set_region(region_code)
        
        if success:
            # Settings saved silently, no popup
            self.dialog.destroy()
        else:
            messagebox.showerror("Error", "Failed to save settings")
