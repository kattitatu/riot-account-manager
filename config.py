"""
Configuration file for Riot Account Manager
"""
import os
import json

CONFIG_FILE = "config.json"

def load_config():
    """Load configuration from file"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
    return {}

def save_config(config):
    """Save configuration to file"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False

def get_api_key():
    """Get Riot API key from config or environment"""
    config = load_config()
    return config.get('riot_api_key') or os.getenv('RIOT_API_KEY')

def set_api_key(api_key):
    """Set Riot API key in config"""
    config = load_config()
    config['riot_api_key'] = api_key
    return save_config(config)

def get_region():
    """Get selected region from config"""
    config = load_config()
    return config.get('region', 'euw1')  # Default to EUW

def set_region(region):
    """Set region in config"""
    config = load_config()
    config['region'] = region
    return save_config(config)

def get_theme():
    """Get selected theme from config"""
    config = load_config()
    return config.get('theme', 'dark_grey')  # Default to current dark grey theme

def set_theme(theme):
    """Set theme in config"""
    config = load_config()
    config['theme'] = theme
    return save_config(config)

def get_theme_colors(theme_name=None):
    """Get color scheme for specified theme"""
    if theme_name is None:
        theme_name = get_theme()
    
    themes = {
        'dark_grey': {
            'bg_primary': '#1e1e1e',
            'bg_secondary': '#2d2d2d',
            'bg_tertiary': '#3a3a3a',
            'text_primary': '#ffffff',
            'text_secondary': '#cccccc',
            'text_muted': '#888888',
            'accent_blue': '#5b9bd5',
            'accent_green': '#00ff88',
            'accent_red': '#ff4444',
            'accent_gold': '#ffd700',
            'border': '#444444',
            'win_bg': '#1a2a3a',
            'win_border': '#4a90e2',
            'loss_bg': '#3a1a1a',
            'loss_border': '#dc3545'
        },
        'pure_black': {
            'bg_primary': '#000000',
            'bg_secondary': '#111111',
            'bg_tertiary': '#222222',
            'text_primary': '#ffffff',
            'text_secondary': '#cccccc',
            'text_muted': '#666666',
            'accent_blue': '#4a90e2',
            'accent_green': '#00cc66',
            'accent_red': '#cc3333',
            'accent_gold': '#ccaa00',
            'border': '#333333',
            'win_bg': '#001122',
            'win_border': '#0066cc',
            'loss_bg': '#220011',
            'loss_border': '#cc0033'
        },
        'bright': {
            'bg_primary': '#ffffff',
            'bg_secondary': '#f5f5f5',
            'bg_tertiary': '#e0e0e0',
            'text_primary': '#000000',
            'text_secondary': '#333333',
            'text_muted': '#666666',
            'accent_blue': '#0066cc',
            'accent_green': '#00aa44',
            'accent_red': '#cc3333',
            'accent_gold': '#cc9900',
            'border': '#cccccc',
            'win_bg': '#e6f3ff',
            'win_border': '#0066cc',
            'loss_bg': '#ffe6e6',
            'loss_border': '#cc3333'
        },
        'blue_dark': {
            'bg_primary': '#0f1419',
            'bg_secondary': '#1a2332',
            'bg_tertiary': '#253244',
            'text_primary': '#ffffff',
            'text_secondary': '#b3d9ff',
            'text_muted': '#7799bb',
            'accent_blue': '#66ccff',
            'accent_green': '#00ff99',
            'accent_red': '#ff6666',
            'accent_gold': '#ffcc66',
            'border': '#334455',
            'win_bg': '#1a3d5c',
            'win_border': '#66ccff',
            'loss_bg': '#5c1a1a',
            'loss_border': '#ff6666'
        },
        'purple_dark': {
            'bg_primary': '#1a0d26',
            'bg_secondary': '#2d1b3d',
            'bg_tertiary': '#402954',
            'text_primary': '#ffffff',
            'text_secondary': '#e6ccff',
            'text_muted': '#b399cc',
            'accent_blue': '#9966ff',
            'accent_green': '#66ff99',
            'accent_red': '#ff6699',
            'accent_gold': '#ffcc99',
            'border': '#553366',
            'win_bg': '#2d1a4d',
            'win_border': '#9966ff',
            'loss_bg': '#4d1a2d',
            'loss_border': '#ff6699'
        }
    }
    
    return themes.get(theme_name, themes['dark_grey'])
