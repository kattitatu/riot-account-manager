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
