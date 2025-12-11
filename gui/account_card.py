import tkinter as tk
from tkinter import ttk
from rank_icons import RankIcons
import pyperclip
import webbrowser
import os
from PIL import Image, ImageTk
from config import get_theme_colors

class AccountCard(tk.Frame):
    def __init__(self, parent, account, on_switch, on_edit, on_delete, on_save_session, on_refresh_rank, on_show_stats, is_active=False, rank_icons=None, profile_icon_fetcher=None):
        # Get theme colors
        self.colors = get_theme_colors()
        
        super().__init__(parent, bg=self.colors['bg_secondary'], relief=tk.RAISED, borderwidth=1)
        self.account = account
        self.on_switch = on_switch
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_save_session = on_save_session
        self.on_refresh_rank = on_refresh_rank
        self.on_show_stats = on_show_stats
        self.rank_icons = rank_icons or RankIcons()
        self.profile_icon_fetcher = profile_icon_fetcher
        self.icon_reference = None  # Keep reference to prevent garbage collection
        
        self.setup_ui()
    
    def refresh_theme(self):
        """Refresh the account card with new theme colors"""
        # Update theme colors
        self.colors = get_theme_colors()
        
        # Update card background
        self.configure(bg=self.colors['bg_secondary'])
        
        # Recursively update all child widgets
        self._update_widget_colors(self)
    
    def _update_widget_colors(self, widget):
        """Recursively update widget colors"""
        try:
            widget_class = widget.winfo_class()
            
            if widget_class == 'Frame':
                widget.configure(bg=self.colors['bg_secondary'])
                        
            elif widget_class == 'Label':
                # Update label colors based on current background
                current_bg = widget.cget('bg')
                current_fg = widget.cget('fg')
                
                # Update background
                widget.configure(bg=self.colors['bg_secondary'])
                
                # Update foreground based on current color
                if current_fg in ['#aaaaaa', '#888888']:
                    widget.configure(fg=self.colors['text_muted'])
                elif current_fg in ['#00bfff']:
                    widget.configure(fg=self.colors['accent_blue'])
                else:
                    widget.configure(fg=self.colors['text_primary'])
                    
            elif widget_class == 'Button':
                # Update button colors based on current color
                current_bg = widget.cget('bg')
                if current_bg in ['#0078d4', '#5b21b6']:
                    widget.configure(bg=self.colors['accent_blue'], fg=self.colors['text_primary'])
                elif current_bg == '#28a745':
                    widget.configure(bg=self.colors['accent_green'], fg=self.colors['text_primary'])
                elif current_bg in ['#17a2b8', '#6c757d', '#4a4a4a', '#2d2d2d']:
                    widget.configure(bg=self.colors['bg_tertiary'], fg=self.colors['text_primary'])
                    
                # Update active background
                widget.configure(activebackground=self.colors['bg_tertiary'])
            
            # Recursively update children
            for child in widget.winfo_children():
                self._update_widget_colors(child)
                
        except tk.TclError:
            # Widget might be destroyed, skip it
            pass
    
    def setup_ui(self):
        """Setup the account card UI"""
        # Padding frame
        content = tk.Frame(self, bg=self.colors['bg_secondary'])
        content.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header frame with name and op.gg button
        header_frame = tk.Frame(content, bg=self.colors['bg_secondary'])
        header_frame.pack(fill=tk.X, pady=(0, 6))
        
        # Left side frame for display name and profile icon
        left_frame = tk.Frame(header_frame, bg=self.colors['bg_secondary'])
        left_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        # Display name
        name_label = tk.Label(left_frame, text=self.account.get("display_name", "Unknown"), 
                             font=("Arial", 12, "bold"), bg=self.colors['bg_secondary'], fg=self.colors['text_primary'])
        name_label.pack(anchor="w")
        
        # Profile icon and level row (below display name)
        profile_icon_id = self.account.get("profile_icon_id")
        summoner_level = self.account.get("summoner_level")
        if profile_icon_id or summoner_level:
            self.display_profile_info(left_frame, profile_icon_id, summoner_level)
        
        # Right side frame for op.gg button and rank icon
        right_frame = tk.Frame(header_frame, bg=self.colors['bg_secondary'])
        right_frame.pack(side=tk.RIGHT, anchor="n")
        
        # op.gg button (aligned with display name)
        riot_id = self.account.get("riot_id", "")
        if riot_id:
            opgg_btn = tk.Button(right_frame, text="op.gg", 
                                command=lambda: self.open_opgg(riot_id),
                                bg=self.colors['accent_blue'], fg=self.colors['text_primary'], font=("Arial", 7, "bold"),
                                padx=5, pady=2, relief=tk.FLAT, cursor="hand2")
            opgg_btn.pack(pady=(0, 2))
        
        # Rank icon (below op.gg button) - clickable
        rank = self.account.get("rank", "")
        if rank:
            rank_icon, rank_color = self.get_rank_icon_and_color(rank)
            self.create_rank_icon_button(right_frame, rank_icon, rank, rank_color)
        
        # Buttons frame
        btn_frame = tk.Frame(content, bg=self.colors['bg_secondary'])
        btn_frame.pack(fill=tk.X, pady=(6, 0))
        
        # Switch button
        switch_btn = tk.Button(btn_frame, text="Switch", 
                              command=self.on_switch,
                              bg=self.colors['accent_blue'], fg=self.colors['text_primary'], font=("Arial", 9, "bold"),
                              padx=8, pady=4, relief=tk.FLAT, cursor="hand2")
        switch_btn.pack(fill=tk.X, pady=(0, 4))
        
        # Bottom buttons row (centered)
        bottom_btn_frame = tk.Frame(content, bg=self.colors['bg_secondary'])
        bottom_btn_frame.pack(fill=tk.X, pady=(4, 0))
        
        # Refresh button
        refresh_btn = tk.Button(bottom_btn_frame, text="Refresh", 
                               command=self.on_refresh_rank,
                               bg=self.colors['bg_tertiary'], fg=self.colors['text_primary'], font=("Arial", 8),
                               padx=8, pady=3, relief=tk.FLAT, cursor="hand2")
        refresh_btn.pack(side=tk.LEFT, padx=(0, 3), expand=True, fill=tk.X)
        
        # Edit button
        edit_btn = tk.Button(bottom_btn_frame, text="Edit", 
                            command=self.on_edit,
                            bg=self.colors['bg_tertiary'], fg=self.colors['text_primary'], font=("Arial", 8),
                            padx=8, pady=3, relief=tk.FLAT, cursor="hand2")
        edit_btn.pack(side=tk.LEFT, padx=(0, 3), expand=True, fill=tk.X)
        
        # Copy Username button
        copy_user_btn = tk.Button(bottom_btn_frame, text="📋 User", 
                                 command=lambda: self.copy_to_clipboard(self.account.get('username', '')),
                                 bg=self.colors['bg_tertiary'], fg=self.colors['text_primary'], font=("Arial", 7),
                                 padx=4, pady=3, relief=tk.FLAT, cursor="hand2")
        copy_user_btn.pack(side=tk.LEFT, padx=(0, 2), expand=True, fill=tk.X)
        
        # Copy Password button (if password exists)
        password = self.account.get('password', '')
        if password:
            copy_pass_btn = tk.Button(bottom_btn_frame, text="📋 Pass", 
                                     command=lambda: self.copy_to_clipboard(password),
                                     bg=self.colors['bg_tertiary'], fg=self.colors['text_primary'], font=("Arial", 7),
                                     padx=4, pady=3, relief=tk.FLAT, cursor="hand2")
            copy_pass_btn.pack(side=tk.LEFT, expand=True, fill=tk.X)
    
    def create_info_row(self, parent, label, value, color):
        """Create an info row with label and value"""
        row = tk.Frame(parent, bg=self.colors['bg_secondary'])
        row.pack(fill=tk.X, pady=1)
        
        label_widget = tk.Label(row, text=label, 
                               font=("Arial", 9), bg=self.colors['bg_secondary'], fg=self.colors['text_muted'])
        label_widget.pack(side=tk.LEFT)
        
        value_widget = tk.Label(row, text=value, 
                               font=("Arial", 9, "bold"), bg=self.colors['bg_secondary'], fg=color)
        value_widget.pack(side=tk.LEFT, padx=(5, 0))
    
    def create_riot_id_row(self, parent, riot_id):
        """Create a Riot ID row with copy button"""
        row = tk.Frame(parent, bg=self.colors['bg_secondary'])
        row.pack(fill=tk.X, pady=1)
        
        label_widget = tk.Label(row, text="Riot ID:", 
                               font=("Arial", 9), bg=self.colors['bg_secondary'], fg=self.colors['text_muted'])
        label_widget.pack(side=tk.LEFT)
        
        value_widget = tk.Label(row, text=riot_id, 
                               font=("Arial", 9, "bold"), bg=self.colors['bg_secondary'], fg=self.colors['accent_blue'])
        value_widget.pack(side=tk.LEFT, padx=(5, 0))
        
        copy_btn = tk.Button(row, text="📋", 
                            command=lambda: self.copy_to_clipboard(riot_id),
                            bg=self.colors['bg_secondary'], fg=self.colors['text_primary'], font=("Arial", 8),
                            padx=3, pady=0, relief=tk.FLAT, cursor="hand2",
                            activebackground=self.colors['bg_tertiary'])
        copy_btn.pack(side=tk.LEFT, padx=(5, 0))
    
    def copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        try:
            pyperclip.copy(text)
        except Exception as e:
            print(f"Error copying to clipboard: {e}")
    
    def display_profile_info(self, parent, icon_id, summoner_level):
        """Display profile icon and summoner level"""
        # Create horizontal frame for icon and level
        profile_frame = tk.Frame(parent, bg=self.colors['bg_secondary'])
        profile_frame.pack(anchor="w", pady=(4, 0))
        
        # Profile icon
        if icon_id and self.profile_icon_fetcher:
            try:
                icon_path = self.profile_icon_fetcher.get_icon_path(icon_id)
                
                if icon_path and os.path.exists(icon_path):
                    img = Image.open(icon_path)
                    img = img.resize((48, 48), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    
                    # Store reference to prevent garbage collection
                    if not hasattr(self, 'profile_icon_reference'):
                        self.profile_icon_reference = photo
                    else:
                        self.profile_icon_reference = photo
                    
                    # Create frame with border for depth effect
                    icon_border = tk.Frame(profile_frame, bg=self.colors['accent_blue'], 
                                          highlightbackground=self.colors['accent_blue'], 
                                          highlightthickness=1)
                    icon_border.pack(side=tk.LEFT, padx=(0, 8))
                    
                    icon_label = tk.Label(icon_border, image=photo, bg=self.colors['bg_secondary'], 
                                         borderwidth=0)
                    icon_label.pack(padx=1, pady=1)
            except Exception as e:
                print(f"Error loading profile icon: {e}")
        
        # Summoner level (only show if not None)
        if summoner_level is not None:
            level_label = tk.Label(profile_frame, text=f"Level: {summoner_level}", 
                                  font=("Arial", 10), bg=self.colors['bg_secondary'], fg=self.colors['text_muted'])
            level_label.pack(side=tk.LEFT, anchor="w")
    
    def open_opgg(self, riot_id):
        """Open op.gg page for the account"""
        # Format: name-tag -> name/tag for op.gg URL
        if "#" in riot_id:
            name, tag = riot_id.split("#", 1)
            url = f"https://www.op.gg/summoners/euw/{name}-{tag}"
        else:
            url = f"https://www.op.gg/summoners/euw/{riot_id}"
        
        try:
            webbrowser.open(url)
        except Exception as e:
            print(f"Error opening op.gg: {e}")
    
    def create_rank_icon_button(self, parent, icon, rank, color):
        """Create a clickable rank icon button"""
        # Try to load PNG icon first
        photo_icon = self.rank_icons.get_rank_icon(rank, size=(48, 48))
        
        if photo_icon:
            # Use PNG icon as button
            self.icon_reference = photo_icon  # Keep reference
            icon_btn = tk.Button(parent, image=photo_icon, bg=self.colors['bg_secondary'], 
                                relief=tk.FLAT, cursor="hand2", 
                                activebackground=self.colors['bg_tertiary'],
                                command=self.on_show_stats)
            icon_btn.pack(pady=(2, 0))
        else:
            # Fallback to emoji icon button
            icon_btn = tk.Button(parent, text=icon, 
                                font=("Arial", 18), bg=self.colors['bg_secondary'], fg=color,
                                relief=tk.FLAT, cursor="hand2",
                                activebackground=self.colors['bg_tertiary'],
                                command=self.on_show_stats)
            icon_btn.pack(pady=(2, 0))
    
    def create_rank_row(self, parent, icon, rank, color):
        """Create a rank row with icon and rank text"""
        row = tk.Frame(parent, bg=self.colors['bg_secondary'])
        row.pack(fill=tk.X, pady=1)
        
        # Try to load PNG icon first
        photo_icon = self.rank_icons.get_rank_icon(rank, size=(48, 48))
        
        if photo_icon:
            # Use PNG icon
            self.icon_reference = photo_icon  # Keep reference
            icon_widget = tk.Label(row, image=photo_icon, bg=self.colors['bg_secondary'])
            icon_widget.pack(side=tk.LEFT, padx=(0, 8))
        else:
            # Fallback to emoji icon
            icon_widget = tk.Label(row, text=icon, 
                                  font=("Arial", 16), bg=self.colors['bg_secondary'], fg=color)
            icon_widget.pack(side=tk.LEFT, padx=(0, 5))
        
        # Rank text
        rank_widget = tk.Label(row, text=rank, 
                              font=("Arial", 11, "bold"), bg=self.colors['bg_secondary'], fg=color)
        rank_widget.pack(side=tk.LEFT)
    
    def get_rank_icon_and_color(self, rank):
        """Get icon and color for a rank"""
        rank_lower = rank.lower()
        
        if "iron" in rank_lower:
            return "⚫", "#4a4a4a"  # Gray
        elif "bronze" in rank_lower:
            return "🟤", "#cd7f32"  # Bronze
        elif "silver" in rank_lower:
            return "⚪", "#c0c0c0"  # Silver
        elif "gold" in rank_lower:
            return "🟡", "#ffd700"  # Gold
        elif "platinum" in rank_lower:
            return "💎", "#00d4aa"  # Teal/Cyan
        elif "emerald" in rank_lower:
            return "💚", "#00ff88"  # Emerald green
        elif "diamond" in rank_lower:
            return "💠", "#6495ed"  # Blue
        elif "master" in rank_lower:
            return "🔮", "#a020f0"  # Purple
        elif "grandmaster" in rank_lower:
            return "🔴", "#ff4444"  # Red
        elif "challenger" in rank_lower:
            return "👑", "#f4c430"  # Golden crown
        else:
            return "🎮", "#ffffff"  # Default
