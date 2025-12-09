"""
Live Game Data Fetcher
Uses SPECTATOR-V5 API to get current game information
"""
import requests
import logging

class LiveGameFetcher:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.logger = logging.getLogger(__name__)
        # Ensure logging is configured
        if not logging.getLogger().handlers:
            logging.basicConfig(level=logging.INFO)
    
    def fetch_live_game(self, riot_id, region='euw1'):
        """
        Fetch live game data for a summoner
        Returns: (game_data, error)
        - game_data: dict with game information or None
        - error: error message or None
        """
        if not self.api_key:
            return None, "API key not configured. Please add your Riot API key in Settings."
        
        try:
            # First, get PUUID from Riot ID
            puuid = self._get_puuid_by_riot_id(riot_id, region)
            if not puuid:
                self.logger.error("Could not get PUUID")
                return None, "Could not find summoner"
            
            self.logger.info(f"PUUID: {puuid}")
            
            # Get active game using SPECTATOR-V5 (uses PUUID directly)
            game_data = self._get_active_game(puuid, region)
            
            if not game_data:
                return None, None  # Not in game (not an error)
            
            # Enrich game data with additional player info
            enriched_data = self._enrich_game_data(game_data, region, puuid)
            
            return enriched_data, None
            
        except Exception as e:
            self.logger.error(f"Error fetching live game: {e}", exc_info=True)
            return None, f"Error: {str(e)}"
    
    def _get_puuid_by_riot_id(self, riot_id, region):
        """Get PUUID by Riot ID"""
        if '#' not in riot_id:
            return None
        
        game_name, tag_line = riot_id.split('#', 1)
        
        # Map region to routing value
        routing = self._get_routing_value(region)
        
        try:
            # Get account by Riot ID
            url = f"https://{routing}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
            response = requests.get(url, headers={'X-Riot-Token': self.api_key}, timeout=10)
            
            if response.status_code != 200:
                self.logger.error(f"Account API failed: {response.status_code}")
                return None
            
            account_data = response.json()
            puuid = account_data.get('puuid')
            
            return puuid
            
        except Exception as e:
            self.logger.error(f"Error getting PUUID: {e}", exc_info=True)
            return None
    
    def _get_summoner_id_by_puuid(self, puuid, region):
        """Get encrypted summoner ID from PUUID"""
        try:
            url = f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
            response = requests.get(url, headers={'X-Riot-Token': self.api_key}, timeout=10)
            
            if response.status_code == 200:
                summoner_data = response.json()
                self.logger.info(f"Full summoner response: {summoner_data}")
                
                # Check all possible ID fields
                summoner_id = (summoner_data.get('id') or 
                              summoner_data.get('accountId') or 
                              summoner_data.get('summonerId'))
                
                if not summoner_id:
                    # Log all keys to see what's available
                    self.logger.error(f"No ID field found. Available keys: {list(summoner_data.keys())}")
                else:
                    self.logger.info(f"Found summoner ID: {summoner_id}")
                
                return summoner_id
            
            self.logger.error(f"Summoner API failed: {response.status_code}")
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting summoner ID: {e}")
            return None
    
    def _get_active_game(self, puuid, region):
        """Get active game for summoner"""
        try:
            # Since Riot removed the 'id' field from SUMMONER-V4, we need to use PUUID directly
            # Try SPECTATOR-V4 with PUUID (this might work)
            self.logger.info("Trying SPECTATOR-V4 with PUUID")
            url = f"https://{region}.api.riotgames.com/lol/spectator/v4/active-games/by-summoner/{puuid}"
            response = requests.get(url, headers={'X-Riot-Token': self.api_key}, timeout=10)
            
            self.logger.info(f"SPECTATOR-V4 status: {response.status_code}")
            
            if response.status_code == 404:
                return None  # Not in game
            
            if response.status_code == 200:
                return response.json()
            
            # If V4 doesn't work, try V5
            if response.status_code in [403, 400]:
                self.logger.info("Trying SPECTATOR-V5 with PUUID")
                url = f"https://{region}.api.riotgames.com/lol/spectator/v5/active-games/by-summoner/{puuid}"
                response = requests.get(url, headers={'X-Riot-Token': self.api_key}, timeout=10)
                
                self.logger.info(f"SPECTATOR-V5 status: {response.status_code}")
                
                if response.status_code == 404:
                    return None  # Not in game
                
                if response.status_code == 200:
                    return response.json()
            
            self.logger.warning(f"Spectator API returned {response.status_code}: {response.text[:200] if response.text else 'No response'}")
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting active game: {e}")
            return None
    
    def _enrich_game_data(self, game_data, region, target_puuid):
        """Enrich game data with ranks and champion mastery for all players"""
        participants = game_data.get('participants', [])
        
        enriched_participants = []
        for participant in participants:
            summoner_id = participant.get('summonerId')
            puuid = participant.get('puuid')
            
            self.logger.info(f"Participant keys: {list(participant.keys())}")
            self.logger.info(f"summonerId from participant: {summoner_id}")
            
            # If no summoner ID in participant data, try to get it from PUUID
            if not summoner_id and puuid:
                self.logger.info(f"Trying to get summoner ID from PUUID: {puuid}")
                summoner_id = self._get_summoner_id_by_puuid(puuid, region)
                self.logger.info(f"Got summoner ID: {summoner_id}")
            
            # Get rank data using PUUID (no summoner ID needed!)
            rank_data = None
            if puuid:
                rank_data = self._get_summoner_rank_by_puuid(puuid, region)
            
            # Get champion mastery
            champion_id = participant.get('championId')
            mastery_points = 0
            if puuid:
                mastery_points = self._get_champion_mastery(puuid, champion_id, region)
            
            # Get summoner level
            summoner_level = None
            if puuid:
                summoner_level = self._get_summoner_level(puuid, region)
            
            # Mark if this is the target player
            is_target = (puuid == target_puuid)
            
            enriched_participant = {
                **participant,
                'rank_data': rank_data,
                'mastery_points': mastery_points,
                'summoner_level': summoner_level,
                'is_target': is_target
            }
            
            enriched_participants.append(enriched_participant)
        
        # Add enriched participants back to game data
        game_data['participants'] = enriched_participants
        
        return game_data
    
    def _get_summoner_rank_by_puuid(self, puuid, region):
        """Get ranked data for a summoner using PUUID"""
        if not puuid:
            return None
            
        try:
            # Use PUUID-based endpoint (same as rank_fetcher.py)
            url = f"https://{region}.api.riotgames.com/lol/league/v4/entries/by-puuid/{puuid}"
            response = requests.get(url, headers={'X-Riot-Token': self.api_key}, timeout=10)
            
            if response.status_code == 200:
                entries = response.json()
                # Find Solo/Duo queue rank
                for entry in entries:
                    if entry.get('queueType') == 'RANKED_SOLO_5x5':
                        return {
                            'tier': entry.get('tier'),
                            'rank': entry.get('rank'),
                            'lp': entry.get('leaguePoints'),
                            'wins': entry.get('wins'),
                            'losses': entry.get('losses')
                        }
                return None
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting rank by PUUID: {e}")
            return None
    
    def _get_champion_mastery(self, puuid, champion_id, region):
        """Get champion mastery points for a specific champion"""
        try:
            url = f"https://{region}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/by-champion/{champion_id}"
            response = requests.get(url, headers={'X-Riot-Token': self.api_key}, timeout=10)
            
            if response.status_code == 200:
                mastery_data = response.json()
                return mastery_data.get('championPoints', 0)
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Error getting champion mastery: {e}")
            return 0
    
    def _get_summoner_level(self, puuid, region):
        """Get summoner level from PUUID"""
        try:
            url = f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
            response = requests.get(url, headers={'X-Riot-Token': self.api_key}, timeout=10)
            
            if response.status_code == 200:
                summoner_data = response.json()
                return summoner_data.get('summonerLevel')
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting summoner level: {e}")
            return None
    
    def _get_routing_value(self, region):
        """Get routing value for region"""
        routing_map = {
            'br1': 'americas',
            'eun1': 'europe',
            'euw1': 'europe',
            'jp1': 'asia',
            'kr': 'asia',
            'la1': 'americas',
            'la2': 'americas',
            'na1': 'americas',
            'oc1': 'sea',
            'ph2': 'sea',
            'ru': 'europe',
            'sg2': 'sea',
            'th2': 'sea',
            'tr1': 'europe',
            'tw2': 'sea',
            'vn2': 'sea',
        }
        return routing_map.get(region, 'americas')
    
    def get_game_mode_name(self, queue_id):
        """Get human-readable game mode name"""
        queue_map = {
            0: 'Custom',
            400: 'Normal Draft',
            420: 'Ranked Solo/Duo',
            430: 'Normal Blind',
            440: 'Ranked Flex',
            450: 'ARAM',
            700: 'Clash',
            830: 'Co-op vs AI Intro',
            840: 'Co-op vs AI Beginner',
            850: 'Co-op vs AI Intermediate',
            900: 'ARURF',
            1020: 'One for All',
            1300: 'Nexus Blitz',
            1400: 'Ultimate Spellbook',
            1700: 'Arena',
            1900: 'URF',
        }
        return queue_map.get(queue_id, f'Game Mode {queue_id}')
    
    def format_game_time(self, seconds):
        """Format game time from seconds to MM:SS"""
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}:{secs:02d}"
