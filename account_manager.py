import json
import os
from pathlib import Path
from datetime import datetime

class AccountManager:
    def __init__(self, data_file="accounts.json"):
        self.data_file = data_file
        self.accounts = []
        self.load_accounts()
    
    def load_accounts(self):
        """Load accounts from JSON file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    self.accounts = json.load(f)
            except Exception as e:
                print(f"Error loading accounts: {e}")
                self.accounts = []
        else:
            self.accounts = []
    
    def save_accounts(self):
        """Save accounts to JSON file"""
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.accounts, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving accounts: {e}")
            return False
    
    def add_account(self, username, display_name="", riot_id="", password=""):
        """Add a new account"""
        account = {
            "id": len(self.accounts),
            "username": username,
            "display_name": display_name or username,
            "rank": "Unranked",
            "riot_id": riot_id,
            "password": password,
            "profile_icon_id": None,
            "summoner_level": None,
            "ranked_stats": None,
            "created_at": datetime.now().isoformat()
        }
        self.accounts.append(account)
        self.save_accounts()
        return account
    
    def update_account(self, account_id, **kwargs):
        """Update an existing account"""
        for account in self.accounts:
            if account["id"] == account_id:
                account.update(kwargs)
                self.save_accounts()
                return True
        return False
    
    def delete_account(self, account_id):
        """Delete an account"""
        self.accounts = [acc for acc in self.accounts if acc["id"] != account_id]
        self.save_accounts()
    
    def get_account(self, account_id):
        """Get a specific account"""
        for account in self.accounts:
            if account["id"] == account_id:
                return account
        return None
    
    def get_all_accounts(self):
        """Get all accounts"""
        return self.accounts
