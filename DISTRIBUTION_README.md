# Riot Account Manager

A simple desktop application for managing and switching between multiple Riot Games accounts.

## Features

- 🔄 **Quick Account Switching** - Switch between accounts with one click
- 💾 **Session Saving** - Save login sessions for automatic login
- 🏆 **Rank Display** - Automatically fetch and display League of Legends ranks
- 🎨 **Clean Interface** - Modern, easy-to-use GUI
- 🔒 **Local Storage** - All data stored locally on your computer

## Installation

### Option 1: Standalone Executable (Recommended)
1. Download `RiotAccountManager.exe`
2. (Optional) Download the `assets` folder for rank icons
3. Double-click to run - no installation needed!

### Option 2: Run from Source
1. Install Python 3.7+
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python main.py`

## Quick Start

1. **Add an Account**
   - Click "+ Add Account"
   - Enter your Riot username and password
   - Add a display name (optional)
   - Add your Riot ID (e.g., "PlayerName#EUW") for rank fetching

2. **Switch Accounts**
   - Click "Switch" on any account card
   - First time: Login manually in Riot Client
   - Click 💾 to save the session
   - Next time: Automatic login!

3. **Fetch Rank**
   - Make sure you've added your Riot ID
   - Click 🔄 on the account card
   - Your rank will be fetched and displayed

## Tips

- **Save Sessions**: After logging in for the first time, click the 💾 button to save your session for automatic login next time
- **Rank Icons**: Place rank PNG files in `assets/ranks/` folder for better visuals
- **Backup**: Your accounts are saved in `accounts.json` - back it up to keep your data safe

## Security Note

⚠️ **Important**: Passwords are stored in plain text in `accounts.json`. Keep this file secure and don't share it with anyone.

## Troubleshooting

**"Riot Client not found"**
- Make sure Riot Client is installed in the default location
- Try running as administrator

**"Could not find rank data"**
- Check that your Riot ID is correct (format: Name#TAG)
- Make sure you have played ranked games this season

**Windows Defender blocks the app**
- This is normal for unsigned executables
- Click "More info" → "Run anyway"
- Or add an exception in Windows Defender

## Support

For issues or questions, contact the developer or check the GitHub repository.

## Credits

Developed with ❤️ for the League of Legends community
