import requests
import os

class RankFetcher:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('RIOT_API_KEY')
    
    def fetch_rank(self, riot_id, region='euw1'):
        """Fetch rank for Riot ID (GameName#TAG). Returns: (rank_string, error, ranked_stats_dict)"""
        try:
            if '#' not in riot_id:
                return None, "Invalid Riot ID format. Use: GameName#TAG", None
            
            if not self.api_key:
                return None, "No API key configured. Please add your Riot API key in Settings.", None
            
            game_name, tag = riot_id.split('#', 1)
            print(f"\n=== Fetching rank for {game_name}#{tag} ===")
            
            print("Using Riot API...")
            rank, stats = self._fetch_from_riot_api(game_name, tag, region)
            
            if rank:
                print(f"✓ Success! Found rank: {rank}")
                return rank, None, stats
            else:
                return None, "Could not fetch rank data", None
                
        except Exception as e:
            print(f"Error fetching rank: {e}")
            return None, str(e), None
    
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
            print(f"Fetching account: {account_url}")
            account_response = requests.get(account_url, headers=headers, timeout=10)
            
            if account_response.status_code != 200:
                print(f"Account lookup failed: {account_response.status_code}")
                return None, None
            
            account_data = account_response.json()
            puuid = account_data.get('puuid')
            
            if not puuid:
                print("Could not get PUUID")
                return None, None
            
            print(f"Got PUUID: {puuid}")
            
            league_url = f"https://{region}.api.riotgames.com/lol/league/v4/entries/by-puuid/{puuid}"
            print(f"Fetching ranked data: {league_url}")
            league_response = requests.get(league_url, headers=headers, timeout=10)
            
            if league_response.status_code != 200:
                print(f"League lookup failed: {league_response.status_code}")
                return None, None
            
            entries = league_response.json()
            
            for entry in entries:
                if entry.get('queueType') == 'RANKED_SOLO_5x5':
                    tier = entry.get('tier', 'Unranked')
                    rank = entry.get('rank', '')
                    lp = entry.get('leaguePoints', 0)
                    wins = entry.get('wins', 0)
                    losses = entry.get('losses', 0)
                    
                    rank_string = f"{tier} {rank}" if rank else tier
                    stats = {
                        'tier': tier,
                        'rank': rank,
                        'lp': lp,
                        'wins': wins,
                        'losses': losses
                    }
                    
                    print(f"Found rank: {rank_string} ({lp} LP)")
                    return rank_string, stats
            
            print("No ranked data found (player may be unranked)")
            return "Unranked", None
            
        except Exception as e:
            print(f"Riot API error: {e}")
            return None, None
