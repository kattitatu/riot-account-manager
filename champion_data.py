"""
Champion data helper
Maps champion IDs to names
"""

# Champion ID to Name mapping (Updated from Data Dragon 15.23.1)
CHAMPION_MAP = {
    1: "Annie", 2: "Olaf", 3: "Galio", 4: "Twisted Fate", 5: "Xin Zhao",
    6: "Urgot", 7: "LeBlanc", 8: "Vladimir", 9: "Fiddlesticks", 10: "Kayle",
    11: "Master Yi", 12: "Alistar", 13: "Ryze", 14: "Sion", 15: "Sivir",
    16: "Soraka", 17: "Teemo", 18: "Tristana", 19: "Warwick", 20: "Nunu",
    21: "Miss Fortune", 22: "Ashe", 23: "Tryndamere", 24: "Jax", 25: "Morgana",
    26: "Zilean", 27: "Singed", 28: "Evelynn", 29: "Twitch", 30: "Karthus",
    31: "Cho'Gath", 32: "Amumu", 33: "Rammus", 34: "Anivia", 35: "Shaco",
    36: "Dr. Mundo", 37: "Sona", 38: "Kassadin", 39: "Irelia", 40: "Janna",
    41: "Gangplank", 42: "Corki", 43: "Karma", 44: "Taric", 45: "Veigar",
    48: "Trundle", 50: "Swain", 51: "Caitlyn", 53: "Blitzcrank", 54: "Malphite",
    55: "Katarina", 56: "Nocturne", 57: "Maokai", 58: "Renekton", 59: "Jarvan IV",
    60: "Elise", 61: "Orianna", 62: "Wukong", 63: "Brand", 64: "Lee Sin",
    67: "Vayne", 68: "Rumble", 69: "Cassiopeia", 72: "Skarner", 74: "Heimerdinger",
    75: "Nasus", 76: "Nidalee", 77: "Udyr", 78: "Poppy", 79: "Gragas",
    80: "Pantheon", 81: "Ezreal", 82: "Mordekaiser", 83: "Yorick", 84: "Akali",
    85: "Kennen", 86: "Garen", 89: "Leona", 90: "Malzahar", 91: "Talon",
    92: "Riven", 96: "Kog'Maw", 98: "Shen", 99: "Lux", 101: "Xerath",
    102: "Shyvana", 103: "Ahri", 104: "Graves", 105: "Fizz", 106: "Volibear",
    107: "Rengar", 110: "Varus", 111: "Nautilus", 112: "Viktor", 113: "Sejuani",
    114: "Fiora", 115: "Ziggs", 117: "Lulu", 119: "Draven", 120: "Hecarim",
    121: "Kha'Zix", 122: "Darius", 126: "Jayce", 127: "Lissandra", 131: "Diana",
    133: "Quinn", 134: "Syndra", 136: "Aurelion Sol", 141: "Kayn", 142: "Zoe",
    143: "Zyra", 145: "Kai'Sa", 147: "Seraphine", 150: "Gnar", 154: "Zac",
    157: "Yasuo", 161: "Vel'Koz", 163: "Taliyah", 164: "Camille", 166: "Akshan",
    200: "Bel'Veth", 201: "Braum", 202: "Jhin", 203: "Kindred", 221: "Zeri",
    222: "Jinx", 223: "Tahm Kench", 233: "Briar", 234: "Viego", 235: "Senna",
    236: "Lucian", 238: "Zed", 240: "Kled", 245: "Ekko", 246: "Qiyana",
    254: "Vi", 266: "Aatrox", 267: "Nami", 268: "Azir", 350: "Yuumi",
    360: "Samira", 412: "Thresh", 420: "Illaoi", 421: "Rek'Sai", 427: "Ivern",
    429: "Kalista", 432: "Bard", 497: "Rakan", 498: "Xayah", 516: "Ornn",
    517: "Sylas", 518: "Neeko", 523: "Aphelios", 526: "Rell", 555: "Pyke",
    711: "Vex", 777: "Yone", 799: "Ambessa", 800: "Mel", 804: "Yunara",
    875: "Sett", 876: "Lillia", 887: "Gwen", 888: "Renata Glasc", 893: "Aurora",
    895: "Nilah", 897: "K'Sante", 901: "Smolder", 902: "Milio", 904: "Zaahen",
    910: "Hwei", 950: "Naafiri"
}

def get_champion_name(champion_id):
    """Get champion name from ID"""
    return CHAMPION_MAP.get(champion_id, f"Champion {champion_id}")

def format_mastery_points(points):
    """Format mastery points (e.g., 150000 -> 150k)"""
    if points >= 1000000:
        return f"{points / 1000000:.1f}M"
    elif points >= 1000:
        return f"{points / 1000:.0f}k"
    else:
        return str(points)


# Champion typical roles (simplified for lane detection)
CHAMPION_ROLES = {
    # Top laners
    1: ['MID'], 3: ['TOP', 'SUPPORT'], 4: ['MID'], 5: ['JUNGLE'], 6: ['TOP'],
    7: ['MID'], 8: ['TOP', 'MID'], 9: ['JUNGLE', 'SUPPORT'], 10: ['TOP'],
    11: ['JUNGLE'], 12: ['SUPPORT'], 13: ['MID'], 14: ['TOP'], 15: ['BOT'],
    16: ['SUPPORT'], 17: ['TOP'], 18: ['BOT'], 19: ['JUNGLE'], 20: ['JUNGLE'],
    21: ['BOT'], 22: ['BOT', 'SUPPORT'], 23: ['TOP'], 24: ['TOP', 'JUNGLE'],
    25: ['SUPPORT', 'MID'], 26: ['SUPPORT'], 27: ['TOP'], 28: ['JUNGLE'],
    29: ['BOT', 'JUNGLE'], 30: ['JUNGLE'], 31: ['TOP', 'MID'], 32: ['JUNGLE', 'SUPPORT'],
    33: ['JUNGLE'], 34: ['MID'], 35: ['JUNGLE', 'SUPPORT'], 36: ['TOP', 'JUNGLE'],
    37: ['SUPPORT'], 38: ['MID'], 39: ['TOP', 'MID'], 40: ['SUPPORT'],
    41: ['TOP'], 42: ['MID', 'BOT'], 43: ['SUPPORT'], 44: ['SUPPORT'],
    45: ['MID'], 48: ['TOP', 'JUNGLE'], 50: ['TOP', 'SUPPORT'], 51: ['BOT'],
    53: ['SUPPORT'], 54: ['TOP', 'SUPPORT'], 55: ['MID'], 56: ['JUNGLE'],
    57: ['TOP', 'SUPPORT'], 58: ['TOP'], 59: ['JUNGLE'], 60: ['JUNGLE', 'SUPPORT'],
    61: ['MID'], 62: ['TOP', 'JUNGLE'], 63: ['SUPPORT', 'MID'], 64: ['JUNGLE'],
    67: ['BOT'], 68: ['TOP'], 69: ['MID'], 72: ['JUNGLE'], 74: ['TOP', 'SUPPORT'],
    75: ['TOP'], 76: ['JUNGLE', 'MID'], 77: ['JUNGLE'], 78: ['TOP', 'SUPPORT'],
    79: ['TOP', 'JUNGLE'], 80: ['TOP', 'SUPPORT'], 81: ['BOT', 'MID'],
    82: ['TOP'], 83: ['TOP'], 84: ['TOP', 'MID'], 85: ['TOP'], 86: ['TOP'],
    89: ['SUPPORT'], 90: ['MID'], 91: ['MID'], 92: ['TOP'], 96: ['BOT'],
    98: ['TOP', 'SUPPORT'], 99: ['MID', 'SUPPORT'], 101: ['MID'], 102: ['JUNGLE'],
    103: ['MID'], 104: ['JUNGLE'], 105: ['MID'], 106: ['TOP', 'JUNGLE'],
    107: ['TOP', 'JUNGLE'], 110: ['BOT', 'MID'], 111: ['SUPPORT'], 112: ['MID'],
    113: ['JUNGLE'], 114: ['TOP'], 115: ['MID'], 117: ['SUPPORT'], 119: ['BOT'],
    120: ['JUNGLE'], 121: ['JUNGLE'], 122: ['TOP'], 126: ['TOP', 'MID'],
    127: ['MID'], 131: ['JUNGLE', 'MID'], 133: ['TOP'], 134: ['MID'],
    136: ['MID'], 141: ['JUNGLE'], 142: ['MID'], 143: ['SUPPORT'], 145: ['BOT'],
    147: ['SUPPORT', 'MID'], 150: ['TOP'], 154: ['JUNGLE'], 157: ['MID', 'TOP'],
    161: ['SUPPORT', 'MID'], 163: ['MID', 'JUNGLE'], 164: ['TOP'], 166: ['MID'],
    200: ['JUNGLE'], 201: ['SUPPORT'], 202: ['BOT'], 203: ['JUNGLE'], 221: ['BOT'],
    222: ['BOT'], 223: ['TOP', 'SUPPORT'], 233: ['JUNGLE'], 234: ['JUNGLE'],
    235: ['SUPPORT', 'BOT'], 236: ['BOT'], 238: ['MID'], 240: ['TOP'],
    245: ['JUNGLE', 'MID'], 246: ['JUNGLE', 'MID'], 254: ['JUNGLE'], 266: ['TOP'],
    267: ['SUPPORT'], 268: ['MID'], 350: ['SUPPORT'], 360: ['BOT'], 412: ['SUPPORT'],
    420: ['TOP'], 421: ['JUNGLE'], 427: ['JUNGLE', 'SUPPORT'], 429: ['BOT'],
    432: ['SUPPORT'], 497: ['SUPPORT'], 498: ['BOT'], 516: ['TOP'], 517: ['MID'],
    518: ['MID', 'SUPPORT'], 523: ['BOT'], 526: ['SUPPORT'], 555: ['SUPPORT'],
    711: ['MID'], 777: ['MID', 'TOP'], 799: ['TOP'], 800: ['SUPPORT'],
    804: ['JUNGLE'], 875: ['TOP'], 876: ['JUNGLE'], 887: ['TOP'], 888: ['SUPPORT'],
    893: ['MID'], 895: ['BOT'], 897: ['TOP'], 901: ['BOT', 'MID'],
    902: ['SUPPORT'], 904: ['JUNGLE'], 910: ['MID'], 950: ['MID', 'JUNGLE']
}

def get_champion_roles(champion_id):
    """Get typical roles for a champion"""
    return CHAMPION_ROLES.get(champion_id, [])
