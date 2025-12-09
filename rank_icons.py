from pathlib import Path
from PIL import Image, ImageTk
import tkinter as tk

class RankIcons:
    def __init__(self):
        self.icons_dir = Path("assets/ranks")
        self.icons_cache = {}
        self.default_size = (32, 32)
    
    def get_rank_icon(self, rank, size=None):
        """
        Get a PhotoImage for the given rank
        rank: string like "Platinum IV", "Gold II", etc.
        size: tuple (width, height) for resizing, defaults to (32, 32)
        """
        if size is None:
            size = self.default_size
        
        # Normalize rank name
        rank_lower = rank.lower().strip()
        
        # Extract tier (Iron, Bronze, Silver, etc.)
        tier = None
        for t in ["iron", "bronze", "silver", "gold", "platinum", "emerald", "diamond", "master", "grandmaster", "challenger"]:
            if t in rank_lower:
                tier = t
                break
        
        if not tier:
            return None
        
        # Check cache
        cache_key = f"{tier}_{size[0]}x{size[1]}"
        if cache_key in self.icons_cache:
            return self.icons_cache[cache_key]
        
        # Try to load icon - check multiple naming patterns
        possible_paths = [
            self.icons_dir / f"{tier}.png",
            self.icons_dir / f"Rank={tier.capitalize()}.png",
            self.icons_dir / f"{tier.capitalize()}.png",
        ]
        
        icon_path = None
        for path in possible_paths:
            if path.exists():
                icon_path = path
                break
        
        if not icon_path:
            return None
        
        try:
            # Load and resize image
            img = Image.open(icon_path)
            img = img.resize(size, Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            # Cache it
            self.icons_cache[cache_key] = photo
            
            return photo
        except Exception as e:
            print(f"Error loading rank icon {icon_path}: {e}")
            return None
    
    def get_rank_color(self, rank):
        """Get the color associated with a rank"""
        rank_lower = rank.lower()
        
        if "iron" in rank_lower:
            return "#4a4a4a"
        elif "bronze" in rank_lower:
            return "#cd7f32"
        elif "silver" in rank_lower:
            return "#c0c0c0"
        elif "gold" in rank_lower:
            return "#ffd700"
        elif "platinum" in rank_lower:
            return "#00d4aa"
        elif "emerald" in rank_lower:
            return "#00ff88"
        elif "diamond" in rank_lower:
            return "#6495ed"
        elif "master" in rank_lower:
            return "#a020f0"
        elif "grandmaster" in rank_lower:
            return "#ff4444"
        elif "challenger" in rank_lower:
            return "#f4c430"
        else:
            return "#ffffff"
