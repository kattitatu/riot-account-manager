"""
Live Game Display Component
Displays live game information in op.gg style
"""
import tkinter as tk
from tkinter import ttk
from champion_data import get_champion_name, format_mastery_points
from champion_icon_fetcher import ChampionIconFetcher
from summoner_spell_fetcher import SummonerSpellFetcher
import webbrowser
from PIL import Image, ImageTk

class LiveGameDisplay:
    def __init__(self, parent, game_data, rank_icons=None):
        self.parent = parent
        self.game_data = game_data
        self.rank_icons = rank_icons
        self.champion_icon_fetcher = ChampionIconFetcher()
        self.spell_fetcher = SummonerSpellFetcher()
        self.icon_references = []  # Keep references to prevent garbage collection
        
        self.setup_display()
    
    def setup_display(self):
        """Setup the live game display"""
        # Clear parent
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        # Main container - aligned to left
        main_frame = tk.Frame(self.parent, bg="#1e1e1e")
        main_frame.pack(side=tk.LEFT, anchor="nw", padx=20, pady=20)
        
        # Teams (no header)
        self.create_teams_display(main_frame)
        
        # Spell tracker on the right
        self.create_spell_tracker()
    

    def sort_by_lane(self, players):
        """Sort players by lane position using summoner spells"""
        # Smite spell ID for jungle detection
        SMITE_ID = 11
        
        # Separate jungle from others
        jungle = []
        others = []
        
        for player in players:
            spell1 = player.get('spell1Id')
            spell2 = player.get('spell2Id')
            
            if spell1 == SMITE_ID or spell2 == SMITE_ID:
                jungle.append(player)
            else:
                others.append(player)
        
        # Return in order: first non-jungle (top), then jungle, then rest
        # This assumes API gives them roughly in order
        if len(others) >= 1 and len(jungle) >= 1:
            # Top, Jungle, Mid, Bot, Support
            result = [others[0]] if len(others) > 0 else []
            result.extend(jungle)
            result.extend(others[1:])
            return result
        else:
            # Fallback: just return original order
            return players
    
    def create_teams_display(self, parent):
        """Create teams display (Blue vs Red) with bans stacked on left"""
        teams_frame = tk.Frame(parent, bg="#1e1e1e")
        teams_frame.pack(fill=tk.BOTH, expand=True)
        
        # Separate participants by team
        participants = self.game_data.get('participants', [])
        blue_team = [p for p in participants if p.get('teamId') == 100]
        red_team = [p for p in participants if p.get('teamId') == 200]
        
        # Get bans
        banned_champions = self.game_data.get('bannedChampions', [])
        blue_bans = [b for b in banned_champions if b.get('teamId') == 100]
        red_bans = [b for b in banned_champions if b.get('teamId') == 200]
        
        # Sort teams by lane
        blue_team = self.sort_by_lane(blue_team)
        red_team = self.sort_by_lane(red_team)
        
        # Bans column (left) - stacked vertically
        bans_container = tk.Frame(teams_frame, bg="#1e1e1e")
        bans_container.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Red bans (top)
        red_bans_frame = tk.Frame(bans_container, bg="#1e1e1e")
        red_bans_frame.pack(fill=tk.X, pady=(0, 10))
        
        red_bans_header = tk.Label(red_bans_frame, text="RED BANS", 
                                   font=("Arial", 10, "bold"), bg="#7a1e1e", fg="white")
        red_bans_header.pack(fill=tk.X, pady=(0, 3))
        
        self.create_bans_column(red_bans_frame, red_bans, red_team)
        
        # Blue bans (bottom)
        blue_bans_frame = tk.Frame(bans_container, bg="#1e1e1e")
        blue_bans_frame.pack(fill=tk.X)
        
        blue_bans_header = tk.Label(blue_bans_frame, text="BLUE BANS", 
                                    font=("Arial", 10, "bold"), bg="#1e4d7a", fg="white")
        blue_bans_header.pack(fill=tk.X, pady=(0, 3))
        
        self.create_bans_column(blue_bans_frame, blue_bans, blue_team)
        
        # Blue team (center-left)
        blue_frame = tk.Frame(teams_frame, bg="#1e1e1e")
        blue_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        blue_header = tk.Label(blue_frame, text="BLUE TEAM", 
                              font=("Arial", 11, "bold"), bg="#1e4d7a", fg="white")
        blue_header.pack(fill=tk.X, pady=(0, 3))
        
        for player in blue_team:
            self.create_player_card(blue_frame, player, "#1e4d7a")
        
        # Red team (center-right)
        red_frame = tk.Frame(teams_frame, bg="#1e1e1e")
        red_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        red_header = tk.Label(red_frame, text="RED TEAM", 
                             font=("Arial", 11, "bold"), bg="#7a1e1e", fg="white")
        red_header.pack(fill=tk.X, pady=(0, 3))
        
        for player in red_team:
            self.create_player_card(red_frame, player, "#7a1e1e")
    
    def create_player_card(self, parent, player, team_color):
        """Create a player card"""
        is_target = player.get('is_target', False)
        
        # Card frame with highlight for target player
        card_bg = "#3d3d3d" if is_target else "#2d2d2d"
        border_color = "#ffd700" if is_target else "#1e1e1e"
        
        card_frame = tk.Frame(parent, bg=border_color, relief=tk.RAISED, borderwidth=2)
        card_frame.pack(fill=tk.X, pady=1)
        
        inner_frame = tk.Frame(card_frame, bg=card_bg)
        inner_frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
        # Player info row
        info_row = tk.Frame(inner_frame, bg=card_bg)
        info_row.pack(fill=tk.X, padx=8, pady=5)
        
        # Summoner spells (stacked vertically on left)
        spell1_id = player.get('spell1Id')
        spell2_id = player.get('spell2Id')
        
        if spell1_id or spell2_id:
            spell_frame = tk.Frame(info_row, bg=card_bg)
            spell_frame.pack(side=tk.LEFT, padx=(0, 3))
            
            # Spell 1 (top)
            if spell1_id:
                spell1_path = self.spell_fetcher.get_spell_icon_path(spell1_id)
                if spell1_path:
                    try:
                        img = Image.open(spell1_path)
                        img = img.resize((16, 16), Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(img)
                        self.icon_references.append(photo)
                        
                        spell1_label = tk.Label(spell_frame, image=photo, bg=card_bg)
                        spell1_label.pack()
                    except Exception as e:
                        print(f"Error loading spell icon: {e}")
            
            # Spell 2 (bottom)
            if spell2_id:
                spell2_path = self.spell_fetcher.get_spell_icon_path(spell2_id)
                if spell2_path:
                    try:
                        img = Image.open(spell2_path)
                        img = img.resize((16, 16), Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(img)
                        self.icon_references.append(photo)
                        
                        spell2_label = tk.Label(spell_frame, image=photo, bg=card_bg)
                        spell2_label.pack()
                    except Exception as e:
                        print(f"Error loading spell icon: {e}")
        
        # Champion icon
        champion_id = player.get('championId')
        champion_name = get_champion_name(champion_id)
        
        icon_path = self.champion_icon_fetcher.get_champion_icon_path(champion_id)
        if icon_path:
            try:
                img = Image.open(icon_path)
                img = img.resize((32, 32), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.icon_references.append(photo)
                
                icon_label = tk.Label(info_row, image=photo, bg=card_bg)
                icon_label.pack(side=tk.LEFT, padx=(0, 5))
            except Exception as e:
                print(f"Error loading champion icon: {e}")
        
        # Champion name
        champ_label = tk.Label(info_row, text=champion_name, 
                              font=("Arial", 9, "bold"), bg=card_bg, fg="white")
        champ_label.pack(side=tk.LEFT)
        
        # Summoner name (clickable) - detect streamer mode
        summoner_name = player.get('riotId', player.get('summonerName', ''))
        
        # Check if streamer mode is enabled (name matches champion name or is empty)
        is_streamer_mode = (not summoner_name or 
                           summoner_name == champion_name or 
                           summoner_name == 'Unknown' or
                           '#' not in summoner_name)
        
        if is_streamer_mode:
            # Streamer mode - show champion name and indicator
            name_label = tk.Label(info_row, text="🎭 Streamer Mode", 
                                 font=("Arial", 8, "italic"), bg=card_bg, fg="#888888")
            name_label.pack(side=tk.LEFT, padx=(8, 0))
        else:
            # Normal mode - show clickable name
            name_label = tk.Label(info_row, text=summoner_name, 
                                 font=("Arial", 9, "underline"), bg=card_bg, fg="#00bfff",
                                 cursor="hand2")
            name_label.pack(side=tk.LEFT, padx=(8, 0))
            
            # Make name clickable to open op.gg
            name_label.bind("<Button-1>", lambda e: self.open_opgg(summoner_name))
        
        # Summoner level (on the right)
        summoner_level = player.get('summoner_level')
        if summoner_level:
            level_label = tk.Label(info_row, text=f"Lvl {summoner_level}", 
                                  font=("Arial", 8, "bold"), bg=card_bg, fg="#00ff88")
            level_label.pack(side=tk.RIGHT)
        
        # Stats row
        stats_row = tk.Frame(inner_frame, bg=card_bg)
        stats_row.pack(fill=tk.X, padx=8, pady=(0, 5))
        
        # Rank with icon
        rank_data = player.get('rank_data')
        if rank_data:
            tier = rank_data.get('tier', 'Unranked')
            rank = rank_data.get('rank', '')
            lp = rank_data.get('lp', 0)
            wins = rank_data.get('wins', 0)
            losses = rank_data.get('losses', 0)
            
            rank_text = f"{tier} {rank}" if rank else tier
            winrate = int((wins / (wins + losses) * 100)) if (wins + losses) > 0 else 0
            
            # Rank icon (small)
            if self.rank_icons:
                rank_icon = self.rank_icons.get_rank_icon(rank_text, size=(20, 20))
                if rank_icon:
                    self.icon_references.append(rank_icon)
                    icon_label = tk.Label(stats_row, image=rank_icon, bg=card_bg)
                    icon_label.pack(side=tk.LEFT, padx=(0, 3))
            
            rank_label = tk.Label(stats_row, text=f"{rank_text} ({lp} LP)", 
                                 font=("Arial", 8), bg=card_bg, fg="#00bfff")
            rank_label.pack(side=tk.LEFT)
            
            wr_label = tk.Label(stats_row, text=f"{wins}W {losses}L ({winrate}%)", 
                               font=("Arial", 8), bg=card_bg, fg="#888888")
            wr_label.pack(side=tk.LEFT, padx=(8, 0))
        else:
            rank_label = tk.Label(stats_row, text="Unranked", 
                                 font=("Arial", 8), bg=card_bg, fg="#888888")
            rank_label.pack(side=tk.LEFT)
        
        # Champion mastery
        mastery_points = player.get('mastery_points', 0)
        if mastery_points > 0:
            mastery_text = format_mastery_points(mastery_points)
            mastery_label = tk.Label(stats_row, text=f"🏆 {mastery_text}", 
                                    font=("Arial", 8), bg=card_bg, fg="#ffd700")
            mastery_label.pack(side=tk.RIGHT)

    def open_opgg(self, riot_id):
        """Open op.gg profile for a player"""
        try:
            # Format: name#tag -> name-tag for op.gg URL
            if "#" in riot_id:
                name, tag = riot_id.split("#", 1)
                url = f"https://www.op.gg/summoners/euw/{name}-{tag}"
            else:
                url = f"https://www.op.gg/summoners/euw/{riot_id}"
            
            webbrowser.open(url)
        except Exception as e:
            print(f"Error opening op.gg: {e}")

    def create_bans_column(self, parent, bans, team_players):
        """Create a column showing banned champions"""
        # Match bans to players by pick turn
        for i, ban in enumerate(bans[:5]):  # Max 5 bans per team
            champion_id = ban.get('championId', -1)
            pick_turn = ban.get('pickTurn', i)
            
            # Create ban card
            ban_frame = tk.Frame(parent, bg="#2d2d2d", relief=tk.RAISED, borderwidth=1)
            ban_frame.pack(fill=tk.X, pady=1)
            
            if champion_id > 0:
                champion_name = get_champion_name(champion_id)
                
                ban_label = tk.Label(ban_frame, text=champion_name, 
                                    font=("Arial", 8), bg="#2d2d2d", fg="#ff6b6b",
                                    wraplength=80)
                ban_label.pack(padx=5, pady=3)
            else:
                # No ban
                ban_label = tk.Label(ban_frame, text="No Ban", 
                                    font=("Arial", 8), bg="#2d2d2d", fg="#666666")
                ban_label.pack(padx=5, pady=3)
        
        # Fill remaining slots if less than 5 bans
        for i in range(len(bans), 5):
            ban_frame = tk.Frame(parent, bg="#2d2d2d", relief=tk.RAISED, borderwidth=1)
            ban_frame.pack(fill=tk.X, pady=1)
            
            ban_label = tk.Label(ban_frame, text="—", 
                                font=("Arial", 8), bg="#2d2d2d", fg="#666666")
            ban_label.pack(padx=5, pady=3)
    
    def create_spell_tracker(self):
        """Create summoner spell tracker for enemy team"""
        # Cosmic Insight rune ID
        self.COSMIC_INSIGHT_ID = 8347
        
        # Spell cooldowns (in seconds)
        self.spell_cooldowns = {
            4: {"name": "Flash", "cd": 300, "cd_cosmic": 250},
            7: {"name": "Heal", "cd": 230, "cd_cosmic": 200},
            21: {"name": "Barrier", "cd": 175, "cd_cosmic": 150},
            14: {"name": "Ignite", "cd": 175, "cd_cosmic": 150},
            3: {"name": "Exhaust", "cd": 230, "cd_cosmic": 200},
        }
        
        # Tracker container on the right
        tracker_frame = tk.Frame(self.parent, bg="#1e1e1e")
        tracker_frame.pack(side=tk.LEFT, anchor="nw", padx=(10, 20), pady=20)
        
        # Header
        header = tk.Label(tracker_frame, text="SPELL TRACKER", 
                         font=("Arial", 12, "bold"), bg="#7a1e1e", fg="white")
        header.pack(fill=tk.X, pady=(0, 10))
        
        # Find the target player's team and get enemy team
        participants = self.game_data.get('participants', [])
        target_player = next((p for p in participants if p.get('is_target')), None)
        
        if target_player:
            # Get enemy team (opposite of target's team)
            my_team_id = target_player.get('teamId')
            enemy_team_id = 200 if my_team_id == 100 else 100
            enemy_team = [p for p in participants if p.get('teamId') == enemy_team_id]
        else:
            # Fallback: show red team if no target found
            enemy_team = [p for p in participants if p.get('teamId') == 200]
        
        enemy_team = self.sort_by_lane(enemy_team)
        
        # Store spell tracking data
        self.spell_timers = {}
        
        # Create tracker for each enemy
        for player in enemy_team:
            self.create_player_spell_tracker(tracker_frame, player)
    
    def create_player_spell_tracker(self, parent, player):
        """Create spell tracker for a single player"""
        champion_id = player.get('championId')
        champion_name = get_champion_name(champion_id)
        spell1_id = player.get('spell1Id')
        spell2_id = player.get('spell2Id')
        
        # Check if player has Cosmic Insight
        has_cosmic = self.has_cosmic_insight(player)
        
        # Player frame
        player_frame = tk.Frame(parent, bg="#2d2d2d", relief=tk.RAISED, borderwidth=1)
        player_frame.pack(fill=tk.X, pady=4)
        
        content_frame = tk.Frame(player_frame, bg="#2d2d2d")
        content_frame.pack(fill=tk.X, padx=10, pady=8)
        
        # Champion icon
        icon_path = self.champion_icon_fetcher.get_champion_icon_path(champion_id)
        if icon_path:
            try:
                img = Image.open(icon_path)
                img = img.resize((40, 40), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.icon_references.append(photo)
                
                icon_label = tk.Label(content_frame, image=photo, bg="#2d2d2d")
                icon_label.pack(side=tk.LEFT, padx=(0, 10))
            except Exception as e:
                print(f"Error loading champion icon: {e}")
        
        # Spells container (horizontal)
        spells_frame = tk.Frame(content_frame, bg="#2d2d2d")
        spells_frame.pack(side=tk.LEFT)
        
        # Track both spells
        for spell_id in [spell1_id, spell2_id]:
            if spell_id in self.spell_cooldowns:
                self.create_spell_button(spells_frame, player, spell_id, has_cosmic)
    
    def has_cosmic_insight(self, player):
        """Check if player has Cosmic Insight rune"""
        perks = player.get('perks', {})
        perk_ids = perks.get('perkIds', [])
        return self.COSMIC_INSIGHT_ID in perk_ids
    
    def create_spell_button(self, parent, player, spell_id, has_cosmic):
        """Create clickable spell button with timer"""
        spell_info = self.spell_cooldowns[spell_id]
        player_id = player.get('summonerId', player.get('puuid', ''))
        
        # Use cosmic cooldown if player has the rune
        cooldown = spell_info['cd_cosmic'] if has_cosmic else spell_info['cd']
        
        # Container for spell icon and timer
        spell_container = tk.Frame(parent, bg="#2d2d2d")
        spell_container.pack(side=tk.LEFT, padx=4)
        
        # Spell icon button
        spell_path = self.spell_fetcher.get_spell_icon_path(spell_id)
        if spell_path:
            try:
                img = Image.open(spell_path)
                img = img.resize((36, 36), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.icon_references.append(photo)
                
                # Create button
                spell_btn = tk.Label(spell_container, image=photo, bg="#2d2d2d", 
                                    cursor="hand2", relief=tk.RAISED, borderwidth=2)
                spell_btn.pack()
                
                # Timer label (on top of icon) - make it transparent to clicks
                timer_label = tk.Label(spell_container, text="", 
                                      font=("Arial", 12, "bold"), bg="#2d2d2d", fg="#ff4444")
                timer_label.place(in_=spell_btn, relx=0.5, rely=0.5, anchor="center")
                
                # Store references
                key = f"{player_id}_{spell_id}"
                self.spell_timers[key] = {
                    'button': spell_btn,
                    'timer_label': timer_label,
                    'original_photo': photo,
                    'cooldown': cooldown,
                    'remaining': 0,
                    'active': False
                }
                
                # Click handler on both button and timer label (so clicks pass through)
                spell_btn.bind("<Button-1>", lambda e, k=key: self.toggle_spell_timer(k))
                timer_label.bind("<Button-1>", lambda e, k=key: self.toggle_spell_timer(k))
                
            except Exception as e:
                print(f"Error loading spell icon: {e}")
    
    def toggle_spell_timer(self, key):
        """Toggle spell timer on/off"""
        timer_data = self.spell_timers.get(key)
        if not timer_data:
            return
        
        if timer_data['active']:
            # Reset timer
            timer_data['active'] = False
            timer_data['remaining'] = 0
            timer_data['timer_label'].config(text="")
            timer_data['button'].config(relief=tk.RAISED)
        else:
            # Start timer
            timer_data['active'] = True
            timer_data['remaining'] = timer_data['cooldown']
            timer_data['button'].config(relief=tk.SUNKEN)
            self.update_spell_timer(key)
    
    def update_spell_timer(self, key):
        """Update spell timer countdown"""
        timer_data = self.spell_timers.get(key)
        if not timer_data or not timer_data['active']:
            return
        
        if timer_data['remaining'] > 0:
            # Show remaining time
            timer_data['timer_label'].config(text=str(timer_data['remaining']))
            timer_data['remaining'] -= 1
            
            # Schedule next update
            self.parent.after(1000, lambda: self.update_spell_timer(key))
        else:
            # Timer finished
            timer_data['active'] = False
            timer_data['timer_label'].config(text="✓", fg="#00ff00")
            timer_data['button'].config(relief=tk.RAISED)
            
            # Clear checkmark after 2 seconds
            self.parent.after(2000, lambda: timer_data['timer_label'].config(text=""))
