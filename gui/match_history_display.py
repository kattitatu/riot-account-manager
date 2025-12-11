"""
Match history display component
"""
import tkinter as tk
from datetime import datetime
from PIL import Image, ImageTk
import os
import requests
import webbrowser
from champion_data import get_champion_roles
from config import get_theme_colors

class MatchHistoryDisplay:
    def __init__(self, parent, matches):
        self.parent = parent
        self.matches = matches
        self.champion_icons = {}  # Cache for champion icons
        self.small_champion_icons = {}  # Cache for small champion icons
        self.item_icons = {}  # Cache for item icons
        self.spell_icons = {}  # Cache for summoner spell icons
        
        # Get theme colors
        self.colors = get_theme_colors()
        
        # Clear parent
        for widget in parent.winfo_children():
            widget.destroy()
        
        # Create scrollable frame
        self.setup_scrollable_frame()
        
        # Display matches
        self.display_matches()
    
    def refresh_theme(self):
        """Refresh the match history display with new theme colors"""
        # Update theme colors
        self.colors = get_theme_colors()
        
        # Update canvas and frame colors
        self.canvas.configure(bg=self.colors['bg_primary'])
        self.scrollable_frame.configure(bg=self.colors['bg_primary'])
        
        # Clear and recreate the display with new colors
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        self.display_matches()
    
    def setup_scrollable_frame(self):
        """Setup scrollable frame for match list"""
        # Canvas for scrolling (no scrollbar)
        self.canvas = tk.Canvas(self.parent, bg=self.colors['bg_primary'], highlightthickness=0)
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.colors['bg_primary'])
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # Center the content horizontally
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="n")
        
        # Update window position when canvas is resized to keep content centered
        def on_canvas_configure(event):
            canvas_width = event.width
            self.canvas.coords(self.canvas.find_all()[0], canvas_width // 2, 0)
        
        self.canvas.bind("<Configure>", on_canvas_configure)
        
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Mouse wheel scrolling
        def on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        self.canvas.bind_all("<MouseWheel>", on_mousewheel)
    
    def display_matches(self):
        """Display all matches"""
        if not self.matches:
            no_matches = tk.Label(self.scrollable_frame, 
                                 text="No matches found", 
                                 font=("Arial", 14), bg=self.colors['bg_primary'], fg=self.colors['text_muted'])
            no_matches.pack(pady=50)
            return
        
        for idx, match in enumerate(self.matches):
            self.create_match_card(match, idx)
    
    def create_match_card(self, match, index):
        """Create a card for a single match"""
        # Determine win/loss colors
        win = match.get('win', False)
        bg_color = self.colors['win_bg'] if win else self.colors['loss_bg']
        border_color = self.colors['win_border'] if win else self.colors['loss_border']
        result_text = "Victory" if win else "Defeat"
        result_color = self.colors['win_border'] if win else self.colors['loss_border']
        
        # Main card frame
        card = tk.Frame(self.scrollable_frame, bg=bg_color, 
                       highlightbackground=border_color, highlightthickness=2)
        card.pack(fill=tk.X, pady=8, padx=5)
        
        # Content frame
        content = tk.Frame(card, bg=bg_color)
        content.pack(fill=tk.BOTH, expand=True, padx=15, pady=12)
        
        # Create a centered container
        centered_container = tk.Frame(content, bg=bg_color)
        centered_container.pack(expand=True, fill=tk.BOTH)
        
        # Left section: Game info (mode, time, result, duration)
        left_section = tk.Frame(centered_container, bg=bg_color)
        left_section.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        
        # Row 1: Game mode
        game_mode = match.get('game_mode', 'Unknown')
        mode_label = tk.Label(left_section, text=game_mode, 
                             font=("Arial", 12, "bold"), bg=bg_color, fg="#5b9bd5")
        mode_label.pack(anchor="w", pady=(0, 2))
        
        # Row 2: Time ago
        time_ago = self.get_time_ago(match.get('game_creation', 0))
        time_label = tk.Label(left_section, text=time_ago, 
                             font=("Arial", 10), bg=bg_color, fg="#888888")
        time_label.pack(anchor="w", pady=(0, 8))
        
        # Separator line
        separator = tk.Frame(left_section, bg="#444444", height=1)
        separator.pack(fill=tk.X, pady=(0, 8))
        
        # Row 3: Result
        result_label = tk.Label(left_section, text=result_text, 
                               font=("Arial", 14, "bold"), bg=bg_color, fg=result_color)
        result_label.pack(anchor="w", pady=(0, 2))
        
        # Row 4: Duration
        duration = match.get('game_duration', 0)
        minutes = duration // 60
        seconds = duration % 60
        duration_text = f"{minutes}m {seconds}s"
        duration_label = tk.Label(left_section, text=duration_text, 
                                 font=("Arial", 10), bg=bg_color, fg="#888888")
        duration_label.pack(anchor="w", pady=(0, 8))
        
        # Champion and stats container
        champion_stats_container = tk.Frame(centered_container, bg=bg_color)
        champion_stats_container.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        
        # Top row: Champion icon and stats side by side
        top_row = tk.Frame(champion_stats_container, bg=bg_color)
        top_row.pack(fill=tk.X)
        
        # Champion icon with level badge (left)
        champion_id = match.get('champion_id')
        champion_name = match.get('champion_name', 'Unknown')
        champion_level = match.get('champion_level', 0)
        
        # Container for icon and level badge overlay
        icon_container = tk.Frame(top_row, bg=bg_color)
        icon_container.pack(side=tk.LEFT)
        
        if champion_id:
            icon = self.get_champion_icon(champion_id, champion_name)
            if icon:
                # Create canvas for icon and level overlay
                canvas = tk.Canvas(icon_container, width=64, height=64, 
                                  bg=bg_color, highlightthickness=0)
                canvas.pack()
                
                # Draw champion icon
                canvas.create_image(0, 0, image=icon, anchor="nw")
                canvas.image = icon  # Keep reference
                
                # Draw level badge (bottom-right corner)
                if champion_level > 0:
                    # Dark circle background
                    canvas.create_oval(38, 38, 64, 64, fill="#1a1a1a", outline="#444444", width=1)
                    
                    # Level text
                    canvas.create_text(51, 51, text=str(champion_level), 
                                     font=("Arial", 11, "bold"), fill="#f0e6d2")
        
        # Summoner spells (between icon and stats)
        spell1_id = match.get('summoner1_id')
        spell2_id = match.get('summoner2_id')
        
        spells_container = tk.Frame(top_row, bg=bg_color)
        spells_container.pack(side=tk.LEFT, padx=(5, 0))
        
        if spell1_id:
            spell1_icon = self.get_spell_icon(spell1_id)
            if spell1_icon:
                spell1_label = tk.Label(spells_container, image=spell1_icon, bg=bg_color)
                spell1_label.image = spell1_icon
                spell1_label.pack()
        
        if spell2_id:
            spell2_icon = self.get_spell_icon(spell2_id)
            if spell2_icon:
                spell2_label = tk.Label(spells_container, image=spell2_icon, bg=bg_color)
                spell2_label.image = spell2_icon
                spell2_label.pack()
        
        # Middle section: KDA, CS
        middle_section = tk.Frame(top_row, bg=bg_color)
        middle_section.pack(side=tk.LEFT, padx=(5, 0))
        
        # Items below champion icon (left-aligned with icon)
        items = match.get('items', [])
        items_frame = tk.Frame(champion_stats_container, bg=bg_color)
        items_frame.pack(anchor="w", pady=(15, 0))
        self.create_items_display(items_frame, items, bg_color)
        
        # KDA row
        kda_row = tk.Frame(middle_section, bg=bg_color)
        kda_row.pack(fill=tk.X, pady=(0, 4))
        
        kills = match.get('kills', 0)
        deaths = match.get('deaths', 0)
        assists = match.get('assists', 0)
        cs = match.get('cs', 0)
        
        # KDA with colored deaths
        kills_label = tk.Label(kda_row, text=str(kills), 
                              font=("Arial", 12, "bold"), bg=bg_color, fg="white")
        kills_label.pack(side=tk.LEFT)
        
        slash1_label = tk.Label(kda_row, text=" / ", 
                               font=("Arial", 12, "bold"), bg=bg_color, fg="white")
        slash1_label.pack(side=tk.LEFT)
        
        deaths_label = tk.Label(kda_row, text=str(deaths), 
                               font=("Arial", 12, "bold"), bg=bg_color, fg="#ff4444")
        deaths_label.pack(side=tk.LEFT)
        
        slash2_label = tk.Label(kda_row, text=" / ", 
                               font=("Arial", 12, "bold"), bg=bg_color, fg="white")
        slash2_label.pack(side=tk.LEFT)
        
        assists_label = tk.Label(kda_row, text=str(assists), 
                                font=("Arial", 12, "bold"), bg=bg_color, fg="white")
        assists_label.pack(side=tk.LEFT)
        
        kda_ratio = (kills + assists) / deaths if deaths > 0 else kills + assists
        kda_ratio_text = f"{kda_ratio:.2f}:1 KDA"
        kda_ratio_label = tk.Label(kda_row, text=kda_ratio_text, 
                                   font=("Arial", 10), bg=bg_color, 
                                   fg=self.get_kda_color(kda_ratio))
        kda_ratio_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # CS row
        cs_row = tk.Frame(middle_section, bg=bg_color)
        cs_row.pack(fill=tk.X)
        
        # Calculate CS per minute
        game_duration = match.get('game_duration', 0)  # in seconds
        cs_per_min = 0
        if game_duration > 0:
            cs_per_min = (cs * 60) / game_duration
        
        cs_text = f"CS {cs} ({cs_per_min:.1f})" if cs_per_min > 0 else f"CS {cs}"
        cs_label = tk.Label(cs_row, text=cs_text, 
                           font=("Arial", 10), bg=bg_color, fg="#aaaaaa")
        cs_label.pack(side=tk.LEFT)
        
        # Right section: Teams
        teams_section = tk.Frame(centered_container, bg=bg_color)
        teams_section.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.create_teams_section(teams_section, match, bg_color)
    
    def create_items_display(self, parent, items, bg_color):
        """Display item icons"""
        # First 6 items (regular items)
        for i in range(6):
            item_id = items[i] if i < len(items) else 0
            
            if item_id and item_id != 0:
                item_icon = self.get_item_icon(item_id)
                if item_icon:
                    icon_label = tk.Label(parent, image=item_icon, bg=bg_color)
                    icon_label.image = item_icon
                    icon_label.pack(side=tk.LEFT, padx=1)
                else:
                    # Empty slot placeholder
                    empty = tk.Frame(parent, bg="#333333", width=28, height=28)
                    empty.pack(side=tk.LEFT, padx=1)
                    empty.pack_propagate(False)
            else:
                # Empty slot placeholder
                empty = tk.Frame(parent, bg="#333333", width=28, height=28)
                empty.pack(side=tk.LEFT, padx=1)
                empty.pack_propagate(False)
        
        # Separator
        separator = tk.Frame(parent, bg="#555555", width=2, height=28)
        separator.pack(side=tk.LEFT, padx=3)
        
        # Trinket/Ward (item slot 6)
        trinket_id = items[6] if len(items) > 6 else 0
        
        if trinket_id and trinket_id != 0:
            trinket_icon = self.get_item_icon(trinket_id)
            if trinket_icon:
                icon_label = tk.Label(parent, image=trinket_icon, bg=bg_color)
                icon_label.image = trinket_icon
                icon_label.pack(side=tk.LEFT)
            else:
                # Empty trinket slot
                empty = tk.Frame(parent, bg="#333333", width=28, height=28)
                empty.pack(side=tk.LEFT)
                empty.pack_propagate(False)
        else:
            # Empty trinket slot
            empty = tk.Frame(parent, bg="#333333", width=28, height=28)
            empty.pack(side=tk.LEFT)
            empty.pack_propagate(False)
    
    def create_teams_section(self, parent, match, bg_color):
        """Create teams display with champion icons and names"""
        blue_team = match.get('blue_team', [])
        red_team = match.get('red_team', [])
        player_team_id = match.get('player_team_id')
        
        # Sort teams by lane
        blue_team = self.sort_by_lane(blue_team)
        red_team = self.sort_by_lane(red_team)
        
        # Blue team (player's team on left)
        if player_team_id == 100:
            self.create_team_column(parent, blue_team, bg_color, is_player_team=True)
        else:
            self.create_team_column(parent, red_team, bg_color, is_player_team=False)
        
        # Separator
        separator = tk.Frame(parent, bg="#444444", width=2)
        separator.pack(side=tk.LEFT, fill=tk.Y, padx=8)
        
        # Red team (enemy team on right)
        if player_team_id == 100:
            self.create_team_column(parent, red_team, bg_color, is_player_team=False)
        else:
            self.create_team_column(parent, blue_team, bg_color, is_player_team=False)
    
    def create_team_column(self, parent, team, bg_color, is_player_team):
        """Create a column showing team champions"""
        team_frame = tk.Frame(parent, bg=bg_color)
        team_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        for player in team:
            player_row = tk.Frame(team_frame, bg=bg_color)
            player_row.pack(fill=tk.X, pady=0)
            
            # Small champion icon
            champion_id = player.get('champion_id')
            champion_name = player.get('champion_name', '')
            
            if champion_id:
                small_icon = self.get_small_champion_icon(champion_id, champion_name)
                if small_icon:
                    icon_label = tk.Label(player_row, image=small_icon, bg=bg_color)
                    icon_label.image = small_icon
                    icon_label.pack(side=tk.LEFT, padx=(0, 5))
            
            # Player name (clickable)
            summoner_name = player.get('summoner_name', 'Unknown')
            riot_id = player.get('riot_id', summoner_name)
            is_player = player.get('is_player', False)
            
            # Truncate long names for display
            display_name = summoner_name
            if len(display_name) > 12:
                display_name = display_name[:12] + "..."
            
            name_color = "#00bfff" if is_player else "#5b9bd5"  # Blue for clickable links
            name_font = ("Arial", 8, "bold", "underline") if is_player else ("Arial", 8, "underline")
            
            name_label = tk.Label(player_row, text=display_name, 
                                 font=name_font, bg=bg_color, fg=name_color,
                                 cursor="hand2")
            name_label.pack(side=tk.LEFT)
            
            # Make clickable - bind to open op.gg with full Riot ID
            name_label.bind("<Button-1>", lambda e, rid=riot_id: self.open_opgg(rid))
    
    def open_opgg(self, riot_id):
        """Open op.gg page for a summoner using Riot ID (name#tag)"""
        try:
            # Format: name#tag -> name-tag for op.gg URL
            if '#' in riot_id:
                name, tag = riot_id.split('#', 1)
                formatted_name = f"{name}-{tag}"
            else:
                formatted_name = riot_id
            
            # Replace spaces with %20
            formatted_name = formatted_name.replace(' ', '%20')
            url = f"https://www.op.gg/summoners/euw/{formatted_name}"
            webbrowser.open(url)
        except Exception as e:
            print(f"Error opening op.gg: {e}")
    
    def sort_by_lane(self, players):
        """Sort players by lane using champion roles and summoner spells"""
        SMITE_ID = 11
        TELEPORT_ID = 12
        HEAL_ID = 7
        EXHAUST_ID = 3
        
        lane_assignments = {
            'TOP': [],
            'JUNGLE': [],
            'MID': [],
            'BOT': [],
            'SUPPORT': []
        }
        
        for player in players:
            champion_id = player.get('champion_id')
            spell1 = player.get('spell1_id')
            spell2 = player.get('spell2_id')
            spells = {spell1, spell2}
            
            # Jungle: Has Smite
            if SMITE_ID in spells:
                lane_assignments['JUNGLE'].append(player)
                continue
            
            # Get champion's typical roles
            roles = get_champion_roles(champion_id)
            
            # Support: Has Exhaust or typical support champion
            if EXHAUST_ID in spells or 'SUPPORT' in roles:
                lane_assignments['SUPPORT'].append(player)
            # Bot/ADC: Has Heal
            elif HEAL_ID in spells:
                lane_assignments['BOT'].append(player)
            # Top: Has Teleport or typical top champion
            elif TELEPORT_ID in spells or 'TOP' in roles:
                lane_assignments['TOP'].append(player)
            # Mid: Everything else or typical mid champion
            else:
                lane_assignments['MID'].append(player)
        
        # Build final list in lane order
        result = []
        for lane in ['TOP', 'JUNGLE', 'MID', 'BOT', 'SUPPORT']:
            result.extend(lane_assignments[lane])
        
        # If we have exactly 5 players and all lanes filled, return sorted
        if len(result) == 5:
            return result
        
        # Fallback: return original order if sorting failed
        return players if len(result) != 5 else result
    
    def get_kda_color(self, kda_ratio):
        """Get color based on KDA ratio"""
        if kda_ratio >= 5.0:
            return "#ffd700"  # Gold
        elif kda_ratio >= 3.0:
            return "#00ff88"  # Green
        elif kda_ratio >= 2.0:
            return "#00bfff"  # Blue
        elif kda_ratio >= 1.0:
            return "#aaaaaa"  # Gray
        else:
            return "#ff4444"  # Red
    
    def get_champion_icon(self, champion_id, champion_name):
        """Get champion icon from Data Dragon CDN"""
        # Check cache first
        if champion_id in self.champion_icons:
            return self.champion_icons[champion_id]
        
        try:
            # Create assets directory if it doesn't exist
            assets_dir = os.path.join(os.path.dirname(__file__), '..', 'assets', 'champion')
            os.makedirs(assets_dir, exist_ok=True)
            
            # Check if icon already exists locally
            icon_path = os.path.join(assets_dir, f"{champion_id}.png")
            
            if not os.path.exists(icon_path):
                # Download from Data Dragon CDN
                # Remove special characters from champion name for URL
                url_name = champion_name.replace("'", "").replace(" ", "").replace(".", "")
                url = f"https://ddragon.leagueoflegends.com/cdn/15.1.1/img/champion/{url_name}.png"
                
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    with open(icon_path, 'wb') as f:
                        f.write(response.content)
            
            # Load and resize icon
            if os.path.exists(icon_path):
                img = Image.open(icon_path)
                img = img.resize((64, 64), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                
                # Cache it
                self.champion_icons[champion_id] = photo
                return photo
        
        except Exception as e:
            print(f"Error loading champion icon: {e}")
        
        return None
    
    def get_small_champion_icon(self, champion_id, champion_name):
        """Get small champion icon (24x24) from Data Dragon CDN"""
        # Check cache first
        if champion_id in self.small_champion_icons:
            return self.small_champion_icons[champion_id]
        
        try:
            # Create assets directory if it doesn't exist
            assets_dir = os.path.join(os.path.dirname(__file__), '..', 'assets', 'champion')
            os.makedirs(assets_dir, exist_ok=True)
            
            # Check if icon already exists locally
            icon_path = os.path.join(assets_dir, f"{champion_id}.png")
            
            if not os.path.exists(icon_path):
                # Download from Data Dragon CDN
                url_name = champion_name.replace("'", "").replace(" ", "").replace(".", "")
                url = f"https://ddragon.leagueoflegends.com/cdn/15.1.1/img/champion/{url_name}.png"
                
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    with open(icon_path, 'wb') as f:
                        f.write(response.content)
            
            # Load and resize icon to small size
            if os.path.exists(icon_path):
                img = Image.open(icon_path)
                img = img.resize((24, 24), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                
                # Cache it
                self.small_champion_icons[champion_id] = photo
                return photo
        
        except Exception as e:
            print(f"Error loading small champion icon: {e}")
        
        return None
    
    def get_item_icon(self, item_id):
        """Get item icon from Data Dragon CDN"""
        # Check cache first
        if item_id in self.item_icons:
            return self.item_icons[item_id]
        
        try:
            # Create assets directory if it doesn't exist
            assets_dir = os.path.join(os.path.dirname(__file__), '..', 'assets', 'items')
            os.makedirs(assets_dir, exist_ok=True)
            
            # Check if icon already exists locally
            icon_path = os.path.join(assets_dir, f"{item_id}.png")
            
            if not os.path.exists(icon_path):
                # Download from Data Dragon CDN
                url = f"https://ddragon.leagueoflegends.com/cdn/15.1.1/img/item/{item_id}.png"
                
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    with open(icon_path, 'wb') as f:
                        f.write(response.content)
            
            # Load and resize icon to 28x28
            if os.path.exists(icon_path):
                img = Image.open(icon_path)
                img = img.resize((28, 28), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                
                # Cache it
                self.item_icons[item_id] = photo
                return photo
        
        except Exception as e:
            print(f"Error loading item icon {item_id}: {e}")
        
        return None
    
    def get_spell_icon(self, spell_id):
        """Get summoner spell icon from Data Dragon CDN"""
        # Check cache first
        if spell_id in self.spell_icons:
            return self.spell_icons[spell_id]
        
        # Spell ID to name mapping
        spell_names = {
            1: 'SummonerBoost', 3: 'SummonerExhaust', 4: 'SummonerFlash',
            6: 'SummonerHaste', 7: 'SummonerHeal', 11: 'SummonerSmite',
            12: 'SummonerTeleport', 13: 'SummonerMana', 14: 'SummonerDot',
            21: 'SummonerBarrier', 30: 'SummonerPoroRecall', 31: 'SummonerPoroThrow',
            32: 'SummonerSnowball', 39: 'SummonerSnowURFSnowball_Mark',
            54: 'Summoner_UltBookPlaceholder', 55: 'Summoner_UltBookSmitePlaceholder'
        }
        
        spell_name = spell_names.get(spell_id, f'Summoner{spell_id}')
        
        try:
            # Create assets directory if it doesn't exist
            assets_dir = os.path.join(os.path.dirname(__file__), '..', 'assets', 'spell')
            os.makedirs(assets_dir, exist_ok=True)
            
            # Check if icon already exists locally
            icon_path = os.path.join(assets_dir, f"{spell_id}.png")
            
            if not os.path.exists(icon_path):
                # Download from Data Dragon CDN
                url = f"https://ddragon.leagueoflegends.com/cdn/15.1.1/img/spell/{spell_name}.png"
                
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    with open(icon_path, 'wb') as f:
                        f.write(response.content)
            
            # Load and resize icon to 32x32 (champion icon is 64, so 2 spells = 64)
            if os.path.exists(icon_path):
                img = Image.open(icon_path)
                img = img.resize((32, 32), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                
                # Cache it
                self.spell_icons[spell_id] = photo
                return photo
        
        except Exception as e:
            print(f"Error loading spell icon {spell_id}: {e}")
        
        return None
    

    def get_time_ago(self, game_creation_ms):
        """Calculate how long ago the game was played"""
        if not game_creation_ms:
            return ""
        
        try:
            # Convert milliseconds to seconds
            game_time = datetime.fromtimestamp(game_creation_ms / 1000)
            now = datetime.now()
            diff = now - game_time
            
            days = diff.days
            hours = diff.seconds // 3600
            minutes = (diff.seconds % 3600) // 60
            
            if days > 0:
                if days == 1:
                    return "1 day ago"
                return f"{days} days ago"
            elif hours > 0:
                if hours == 1:
                    return "1 hour ago"
                return f"{hours} hours ago"
            elif minutes > 0:
                if minutes == 1:
                    return "1 minute ago"
                return f"{minutes} minutes ago"
            else:
                return "Just now"
        
        except Exception as e:
            print(f"Error calculating time ago: {e}")
            return ""
