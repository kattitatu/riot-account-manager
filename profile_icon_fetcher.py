import requests
import os
from pathlib import Path

class ProfileIconFetcher:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.cache_dir = Path("assets/profile")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.version = self.get_latest_version()
        self.base_url = f"https://ddragon.leagueoflegends.com/cdn/{self.version}/img/profileicon"
    
    def get_latest_version(self):
        try:
            response = requests.get("https://ddragon.leagueoflegends.com/api/versions.json", timeout=5)
            if response.status_code == 200:
                return response.json()[0]
        except:
            pass
        return "14.23.1"
    
    def fetch_profile_data(self, riot_id, region='euw1'):
        """Returns (icon_id, summoner_level) or (None, None)"""
        try:
            if '#' not in riot_id:
                return None, None
            
            if not self.api_key:
                print("No API key configured")
                return None, None
            
            game_name, tag = riot_id.split('#', 1)
            print(f"Fetching profile data for {game_name}#{tag}")
            
            icon_id, level = self._fetch_from_riot_api(game_name, tag, region)
            if icon_id or level:
                print(f"Got from API - Icon ID: {icon_id}, Level: {level}")
                return icon_id, level
            
            return None, None
            
        except Exception as e:
            print(f"Error fetching profile data: {e}")
            return None, None
    
    def fetch_profile_icon_id(self, riot_id, region='euw1'):
        icon_id, _ = self.fetch_profile_data(riot_id, region)
        return icon_id
    
    def _fetch_from_riot_api(self, game_name, tag, region='euw1'):
        try:
            routing_map = {
                'br1': 'americas', 'eun1': 'europe', 'euw1': 'europe',
                'jp1': 'asia', 'kr': 'asia', 'la1': 'americas', 'la2': 'americas',
                'na1': 'americas', 'oc1': 'sea', 'ph2': 'sea', 'ru': 'europe',
                'sg2': 'sea', 'th2': 'sea', 'tr1': 'europe', 'tw2': 'sea', 'vn2': 'sea'
            }
            routing = routing_map.get(region, 'americas')
            headers = {'X-Riot-Token': self.api_key}
            
            account_url = f"https://{routing}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag}"
            account_response = requests.get(account_url, headers=headers, timeout=10)
            
            if account_response.status_code != 200:
                print(f"Account lookup failed: {account_response.status_code}")
                return None, None
            
            puuid = account_response.json().get('puuid')
            if not puuid:
                return None, None
            
            summoner_url = f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
            summoner_response = requests.get(summoner_url, headers=headers, timeout=10)
            
            if summoner_response.status_code == 200:
                summoner_data = summoner_response.json()
                profile_icon_id = summoner_data.get('profileIconId')
                summoner_level = summoner_data.get('summonerLevel')
                return profile_icon_id, summoner_level
            
            return None, None
            
        except Exception as e:
            print(f"Riot API error: {e}")
            return None, None
    
    def get_icon_path(self, icon_id):
        """Download profile icon from Data Dragon if not cached"""
        if not icon_id:
            return None
        
        icon_path = self.cache_dir / f"{icon_id}.png"
        if icon_path.exists():
            return str(icon_path)
        
        try:
            url = f"{self.base_url}/{icon_id}.png"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                with open(icon_path, 'wb') as f:
                    f.write(response.content)
                print(f"Downloaded profile icon {icon_id}")
                return str(icon_path)
            else:
                print(f"Failed to download profile icon {icon_id}: {response.status_code}")
        except Exception as e:
            print(f"Error downloading profile icon {icon_id}: {e}")
        
        return None
