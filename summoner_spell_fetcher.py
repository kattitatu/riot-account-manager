"""
Summoner Spell Icon Fetcher
Downloads summoner spell icons from Riot Data Dragon CDN
"""
import requests
import os
from pathlib import Path

class SummonerSpellFetcher:
    # Spell ID to name mapping
    SPELL_MAP = {
        1: "Cleanse",
        3: "Exhaust",
        4: "Flash",
        6: "Ghost",
        7: "Heal",
        11: "Smite",
        12: "Teleport",
        13: "Clarity",
        14: "Ignite",
        21: "Barrier",
        30: "To the King!",
        31: "Poro Toss",
        32: "Mark",
        39: "Ultra Rapid Fire",
        54: "Placeholder",
        55: "Placeholder and Attack",
    }
    
    def __init__(self):
        self.cache_dir = Path("assets/spell")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Get latest version
        self.version = self.get_latest_version()
        self.base_url = f"https://ddragon.leagueoflegends.com/cdn/{self.version}/img/spell"
    
    def get_latest_version(self):
        """Get the latest Data Dragon version"""
        try:
            response = requests.get("https://ddragon.leagueoflegends.com/api/versions.json", timeout=5)
            if response.status_code == 200:
                versions = response.json()
                return versions[0]
        except:
            pass
        return "14.23.1"
    
    def get_spell_icon_path(self, spell_id):
        """Get local path for spell icon, download if needed"""
        spell_name = self.SPELL_MAP.get(spell_id)
        if not spell_name:
            return None
        
        # Check if already cached
        icon_path = self.cache_dir / f"{spell_id}.png"
        if icon_path.exists():
            return str(icon_path)
        
        # Download icon
        try:
            # Data Dragon uses specific names
            spell_names = {
                1: "SummonerBoost",
                3: "SummonerExhaust",
                4: "SummonerFlash",
                6: "SummonerHaste",
                7: "SummonerHeal",
                11: "SummonerSmite",
                12: "SummonerTeleport",
                13: "SummonerMana",
                14: "SummonerDot",
                21: "SummonerBarrier",
                32: "SummonerSnowball",
            }
            
            url_name = spell_names.get(spell_id, spell_name.replace(" ", ""))
            url = f"{self.base_url}/{url_name}.png"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                with open(icon_path, 'wb') as f:
                    f.write(response.content)
                return str(icon_path)
        except Exception as e:
            print(f"Error downloading spell icon for {spell_name}: {e}")
        
        return None
