import requests

# Fetch latest champion data from Data Dragon
response = requests.get('https://ddragon.leagueoflegends.com/cdn/15.23.1/data/en_US/champion.json')
data = response.json()['data']

# Convert to ID: Name mapping
champs = {int(v['key']): v['id'] for k, v in data.items()}

# Print in Python dict format
print("CHAMPION_MAP = {")
for champ_id, name in sorted(champs.items()):
    print(f'    {champ_id}: "{name}",')
print("}")
