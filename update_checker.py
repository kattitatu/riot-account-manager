"""
Auto-update checker for Riot Account Manager
Checks GitHub releases for new versions
"""
import requests
import webbrowser
import os
import sys
import subprocess
import tempfile
from pathlib import Path
from version import __version__
from packaging import version as pkg_version

class UpdateChecker:
    def __init__(self, github_repo):
        """
        Initialize update checker
        
        Args:
            github_repo: GitHub repository in format "username/repo"
        """
        self.github_repo = github_repo
        self.current_version = __version__
        self.api_url = f"https://api.github.com/repos/{github_repo}/releases/latest"
    
    def check_for_updates(self):
        """
        Check if a new version is available
        
        Returns:
            tuple: (has_update, latest_version, download_url, release_notes, exe_download_url)
        """
        try:
            response = requests.get(self.api_url, timeout=5)
            
            if response.status_code != 200:
                return False, None, None, None, None
            
            release_data = response.json()
            latest_version = release_data.get('tag_name', '').lstrip('v')
            download_url = release_data.get('html_url')
            release_notes = release_data.get('body', 'No release notes available.')
            
            # Find the .exe file in assets
            exe_download_url = None
            assets = release_data.get('assets', [])
            for asset in assets:
                if asset.get('name', '').endswith('.exe'):
                    exe_download_url = asset.get('browser_download_url')
                    break
            
            # Compare versions
            if self._is_newer_version(latest_version):
                return True, latest_version, download_url, release_notes, exe_download_url
            
            return False, latest_version, download_url, release_notes, exe_download_url
            
        except Exception as e:
            print(f"Error checking for updates: {e}")
            return False, None, None, None, None
    
    def _is_newer_version(self, latest_version):
        """Compare version numbers"""
        try:
            return pkg_version.parse(latest_version) > pkg_version.parse(self.current_version)
        except Exception:
            # Fallback to string comparison if parsing fails
            return latest_version != self.current_version
    
    def open_download_page(self, url):
        """Open the download page in browser"""
        try:
            webbrowser.open(url)
        except Exception as e:
            print(f"Error opening download page: {e}")
    
    def download_and_install_update(self, exe_url, progress_callback=None):
        """
        Download the new version and install it
        
        Args:
            exe_url: Direct download URL for the .exe file
            progress_callback: Optional callback function(downloaded, total)
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Download to temp directory
            temp_dir = tempfile.gettempdir()
            temp_exe = os.path.join(temp_dir, "RiotAccountManager_update.exe")
            
            # Download with progress
            response = requests.get(exe_url, stream=True, timeout=30)
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(temp_exe, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback:
                            progress_callback(downloaded, total_size)
            
            # Create update script
            if getattr(sys, 'frozen', False):
                # Running as exe
                current_exe = sys.executable
            else:
                # Running as script (for testing)
                current_exe = os.path.abspath(__file__)
            
            # Create batch script to replace exe and restart
            batch_script = os.path.join(temp_dir, "update_riot_manager.bat")
            with open(batch_script, 'w') as f:
                f.write('@echo off\n')
                f.write('echo Updating Riot Account Manager...\n')
                f.write('timeout /t 2 /nobreak > nul\n')  # Wait for app to close
                f.write(f'move /Y "{temp_exe}" "{current_exe}"\n')
                f.write('echo Update complete! Restarting...\n')
                f.write('timeout /t 1 /nobreak > nul\n')
                f.write(f'start "" "{current_exe}"\n')
                f.write(f'del "%~f0"\n')  # Delete the batch script itself
            
            # Run the batch script and exit
            subprocess.Popen(['cmd', '/c', batch_script], 
                           creationflags=subprocess.CREATE_NO_WINDOW)
            
            return True
            
        except Exception as e:
            print(f"Error downloading/installing update: {e}")
            return False
