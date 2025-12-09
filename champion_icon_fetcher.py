"""
Champion Icon Fetcher
Downloads champion icons from Riot Data Dragon CDN
"""
import requests
import os
from pathlib import Path
from champion_data import CHAMPION_MAP

class ChampionIconFetcher:
    def __init__(self):
        self.cache_dir = Path("assets/champion")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Get latest version from Data Dragon
        self.version = self.get_latest_version()
        self.base_url = f"https://ddragon.leagueoflegends.com/cdn/{self.version}/img/champion"
    
    def get_latest_version(self):
        """Get the latest Data Dragon version"""
        try:
            response = requests.get("https://ddragon.leagueoflegends.com/api/versions.json", timeout=5)
            if response.status_code == 200:
                versions = response.json()
                return versions[0]  # Latest version
        except:
            pass
        return "14.23.1"  # Fallback version
    
    def get_champion_icon_path(self, champion_id):
        """Get local path for champion icon, download if needed"""
        # Get champion name from ID
        champion_name = CHAMPION_MAP.get(champion_id)
        if not champion_name:
            return None
        
        # Special cases for Data Dragon URLs
        name_mapping = {
            "Wukong": "MonkeyKing",
            "Nunu": "Nunu",
            "Kha'Zix": "Khazix",
            "Cho'Gath": "Chogath",
            "Kog'Maw": "KogMaw",
            "Vel'Koz": "Velkoz",
            "Rek'Sai": "RekSai",
            "Kai'Sa": "Kaisa",
            "Bel'Veth": "Belveth",
            "K'Sante": "KSante",
            "LeBlanc": "Leblanc",
            "Dr. Mundo": "DrMundo",
            "Twisted Fate": "TwistedFate",
            "Jarvan IV": "JarvanIV",
            "Master Yi": "MasterYi",
            "Miss Fortune": "MissFortune",
            "Tahm Kench": "TahmKench",
            "Aurelion Sol": "AurelionSol",
            "Lee Sin": "LeeSin",
            "Xin Zhao": "XinZhao",
            "Renata Glasc": "Renata",
        }
        
        url_name = name_mapping.get(champion_name, champion_name.replace("'", "").replace(" ", "").replace(".", ""))
        
        # Check if already cached
        icon_path = self.cache_dir / f"{champion_id}.png"
        if icon_path.exists():
            return str(icon_path)
        
        # Download icon
        try:
            url = f"{self.base_url}/{url_name}.png"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                with open(icon_path, 'wb') as f:
                    f.write(response.content)
                return str(icon_path)
        except Exception as e:
            print(f"Error downloading champion icon for {champion_name}: {e}")
        
        return None
    
    def preload_icons(self, champion_ids):
        """Preload multiple champion icons in background"""
        for champion_id in champion_ids:
            self.get_champion_icon_path(champion_id)
