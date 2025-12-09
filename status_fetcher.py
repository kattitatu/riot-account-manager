"""
League of Legends Status Fetcher
Uses LOL-STATUS-V4 API to get platform status
"""
import requests
import logging

class StatusFetcher:
    # Region mapping to platform IDs
    REGIONS = {
        'euw1': {'name': 'EUW', 'platform': 'euw1'},
        'eun1': {'name': 'EUNE', 'platform': 'eun1'},
        'na1': {'name': 'NA', 'platform': 'na1'},
        'kr': {'name': 'KR', 'platform': 'kr'},
        'br1': {'name': 'BR', 'platform': 'br1'},
        'la1': {'name': 'LAN', 'platform': 'la1'},
        'la2': {'name': 'LAS', 'platform': 'la2'},
        'oc1': {'name': 'OCE', 'platform': 'oc1'},
        'tr1': {'name': 'TR', 'platform': 'tr1'},
        'ru': {'name': 'RU', 'platform': 'ru'},
        'jp1': {'name': 'JP', 'platform': 'jp1'},
        'ph2': {'name': 'PH', 'platform': 'ph2'},
        'sg2': {'name': 'SG', 'platform': 'sg2'},
        'th2': {'name': 'TH', 'platform': 'th2'},
        'tw2': {'name': 'TW', 'platform': 'tw2'},
        'vn2': {'name': 'VN', 'platform': 'vn2'},
    }
    
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.logger = logging.getLogger(__name__)
    
    def fetch_status(self, region='euw1'):
        """
        Fetch platform status for a region
        Returns: (status, incidents, maintenances)
        - status: 'online', 'degraded', 'offline', or 'unknown'
        - incidents: list of active incidents
        - maintenances: list of scheduled maintenances
        """
        try:
            platform = self.REGIONS.get(region, {}).get('platform', region)
            
            # LOL-STATUS-V4 endpoint
            url = f"https://{platform}.api.riotgames.com/lol/status/v4/platform-data"
            
            headers = {}
            if self.api_key:
                headers['X-Riot-Token'] = self.api_key
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_status(data)
            elif response.status_code == 403:
                self.logger.warning("API key invalid or missing for status check")
                return 'unknown', [], []
            else:
                self.logger.error(f"Status API returned {response.status_code}")
                return 'unknown', [], []
                
        except requests.exceptions.Timeout:
            self.logger.error("Status API request timed out")
            return 'unknown', [], []
        except Exception as e:
            self.logger.error(f"Error fetching status: {e}")
            return 'unknown', [], []
    
    def _parse_status(self, data):
        """Parse status data from API response"""
        incidents = []
        maintenances = []
        overall_status = 'online'
        
        # Parse maintenances
        for maintenance in data.get('maintenances', []):
            maintenance_info = {
                'id': maintenance.get('id'),
                'titles': maintenance.get('titles', []),
                'updates': maintenance.get('updates', []),
                'maintenance_status': maintenance.get('maintenance_status'),
                'incident_severity': maintenance.get('incident_severity'),
            }
            maintenances.append(maintenance_info)
            
            # If there's an active maintenance, status is degraded
            if maintenance.get('maintenance_status') in ['in_progress', 'scheduled']:
                overall_status = 'degraded'
        
        # Parse incidents
        for incident in data.get('incidents', []):
            incident_info = {
                'id': incident.get('id'),
                'titles': incident.get('titles', []),
                'updates': incident.get('updates', []),
                'incident_severity': incident.get('incident_severity'),
            }
            incidents.append(incident_info)
            
            # Determine overall status based on incident severity
            severity = incident.get('incident_severity', 'info')
            if severity == 'critical':
                overall_status = 'offline'
            elif severity in ['warning', 'info'] and overall_status == 'online':
                overall_status = 'degraded'
        
        return overall_status, incidents, maintenances
    
    def get_region_name(self, region_code):
        """Get display name for region code"""
        return self.REGIONS.get(region_code, {}).get('name', region_code.upper())
    
    def get_all_regions(self):
        """Get list of all available regions"""
        return [(code, info['name']) for code, info in self.REGIONS.items()]
