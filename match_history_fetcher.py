"""
Match history fetcher for Riot API
"""
import requests
from config import get_region

class MatchHistoryFetcher:
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {"X-Riot-Token": api_key}
        
        # Region routing values
        self.region_routing = {
            'euw1': 'europe',
            'eun1': 'europe',
            'tr1': 'europe',
            'ru': 'europe',
            'na1': 'americas',
            'br1': 'americas',
            'la1': 'americas',
            'la2': 'americas',
            'kr': 'asia',
            'jp1': 'asia',
            'oc1': 'sea',
            'ph2': 'sea',
            'sg2': 'sea',
            'th2': 'sea',
            'tw2': 'sea',
            'vn2': 'sea'
        }
        
        # Queue type names
        self.queue_names = {
            420: 'Ranked Solo/Duo',
            440: 'Ranked Flex',
            400: 'Normal Draft',
            430: 'Normal Blind',
            450: 'ARAM',
            700: 'Clash',
            900: 'URF',
            1020: 'One For All',
            1300: 'Nexus Blitz',
            1400: 'Ultimate Spellbook'
        }
    
    def get_routing_value(self, region):
        """Get routing value for match-v5 API"""
        return self.region_routing.get(region.lower(), 'europe')
    
    def get_puuid_from_riot_id(self, riot_id, region):
        """Get PUUID from Riot ID"""
        try:
            if '#' not in riot_id:
                return None, "Invalid Riot ID format"
            
            game_name, tag_line = riot_id.split('#', 1)
            routing = self.get_routing_value(region)
            
            url = f"https://{routing}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('puuid'), None
            else:
                return None, f"Failed to get PUUID: {response.status_code}"
        
        except Exception as e:
            return None, f"Error getting PUUID: {str(e)}"
    
    def fetch_match_history(self, riot_id, region, count=10):
        """
        Fetch match history for a player
        
        Returns:
            tuple: (match_list, error)
            match_list: List of match data dictionaries
            error: Error message if any
        """
        try:
            # Get PUUID first
            puuid, error = self.get_puuid_from_riot_id(riot_id, region)
            if error:
                return None, error
            
            routing = self.get_routing_value(region)
            
            # Get match IDs
            match_ids_url = f"https://{routing}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
            params = {'start': 0, 'count': count}
            
            response = requests.get(match_ids_url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code != 200:
                return None, f"Failed to fetch match IDs: {response.status_code}"
            
            match_ids = response.json()
            
            if not match_ids:
                return [], None  # No matches found
            
            # Fetch details for each match
            matches = []
            for match_id in match_ids:
                match_data = self.fetch_match_details(match_id, puuid, routing)
                if match_data:
                    matches.append(match_data)
            
            return matches, None
        
        except Exception as e:
            return None, f"Error fetching match history: {str(e)}"
    
    def fetch_match_details(self, match_id, puuid, routing):
        """Fetch details for a specific match"""
        try:
            url = f"https://{routing}.api.riotgames.com/lol/match/v5/matches/{match_id}"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                return None
            
            match_data = response.json()
            info = match_data.get('info', {})
            
            # Find the player's participant data
            participants = info.get('participants', [])
            player_data = None
            player_team_id = None
            
            for participant in participants:
                if participant.get('puuid') == puuid:
                    player_data = participant
                    player_team_id = participant.get('teamId')
                    break
            
            if not player_data:
                return None
            
            # Extract relevant data
            queue_id = info.get('queueId', 0)
            game_mode = self.queue_names.get(queue_id, f'Queue {queue_id}')
            
            # Calculate LP change for ranked games
            lp_change = None
            if queue_id in [420, 440]:  # Ranked queues
                lp_change = "Win" if player_data.get('win') else "Loss"
            
            # Separate teams
            blue_team = []
            red_team = []
            
            for participant in participants:
                team_id = participant.get('teamId')
                
                # Get Riot ID (name#tag)
                game_name = participant.get('riotIdGameName', participant.get('summonerName', 'Unknown'))
                tag_line = participant.get('riotIdTagline', '')
                riot_id = f"{game_name}#{tag_line}" if tag_line else game_name
                
                player_info = {
                    'champion_id': participant.get('championId'),
                    'champion_name': participant.get('championName'),
                    'summoner_name': game_name,
                    'riot_id': riot_id,
                    'spell1_id': participant.get('summoner1Id'),
                    'spell2_id': participant.get('summoner2Id'),
                    'is_player': participant.get('puuid') == puuid
                }
                
                if team_id == 100:
                    blue_team.append(player_info)
                else:
                    red_team.append(player_info)
            
            # Get player's items
            items = [
                player_data.get('item0', 0),
                player_data.get('item1', 0),
                player_data.get('item2', 0),
                player_data.get('item3', 0),
                player_data.get('item4', 0),
                player_data.get('item5', 0),
                player_data.get('item6', 0)  # Trinket/Ward
            ]
            
            # Get rune data
            perks = player_data.get('perks', {})
            primary_style = perks.get('styles', [{}])[0] if perks.get('styles') else {}
            secondary_style = perks.get('styles', [{}])[1] if len(perks.get('styles', [])) > 1 else {}
            
            # Get keystone (first selection in primary tree)
            keystone_id = primary_style.get('selections', [{}])[0].get('perk', 0) if primary_style.get('selections') else 0
            primary_tree_id = primary_style.get('style', 0)
            secondary_tree_id = secondary_style.get('style', 0)
            
            match_info = {
                'match_id': match_id,
                'champion_id': player_data.get('championId'),
                'champion_name': player_data.get('championName'),
                'champion_level': player_data.get('champLevel', 0),
                'summoner1_id': player_data.get('summoner1Id'),
                'summoner2_id': player_data.get('summoner2Id'),
                'keystone_id': keystone_id,
                'primary_tree_id': primary_tree_id,
                'secondary_tree_id': secondary_tree_id,
                'kills': player_data.get('kills', 0),
                'deaths': player_data.get('deaths', 0),
                'assists': player_data.get('assists', 0),
                'cs': player_data.get('totalMinionsKilled', 0) + player_data.get('neutralMinionsKilled', 0),
                'win': player_data.get('win', False),
                'game_mode': game_mode,
                'queue_id': queue_id,
                'game_duration': info.get('gameDuration', 0),
                'game_creation': info.get('gameCreation', 0),
                'lp_change': lp_change,
                'player_team_id': player_team_id,
                'blue_team': blue_team,
                'red_team': red_team,
                'items': items
            }
            
            return match_info
        
        except Exception as e:
            print(f"Error fetching match details: {e}")
            return None
