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
        Download and install update (works with --onefile PyInstaller)
        
        Args:
            exe_url: Direct download URL for the .exe file
            progress_callback: Optional callback function(downloaded, total)
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get the actual exe location (not temp for --onefile)
            if getattr(sys, 'frozen', False):
                # For --onefile, sys.executable points to temp location
                # We need to find the actual exe location
                import __main__
                if hasattr(__main__, '__file__'):
                    current_exe = os.path.abspath(__main__.__file__)
                else:
                    # Fallback: use sys.argv[0]
                    current_exe = os.path.abspath(sys.argv[0])
            else:
                current_exe = os.path.abspath(__file__)
            
            # Download to same directory as current exe
            exe_dir = os.path.dirname(current_exe)
            temp_exe = os.path.join(exe_dir, "RiotAccountManager_update.exe")
            
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
            
            # Create update batch script with visible window for debugging
            batch_script = os.path.join(exe_dir, "update.bat")
            with open(batch_script, 'w') as f:
                f.write('@echo off\n')
                f.write('title Riot Account Manager Update\n')
                f.write('echo ========================================\n')
                f.write('echo Riot Account Manager Update\n')
                f.write('echo ========================================\n')
                f.write('echo.\n')
                f.write('echo Waiting for application to close...\n')
                f.write('timeout /t 5 /nobreak\n')
                f.write('echo.\n')
                f.write('echo Updating executable...\n')
                f.write(f':retry\n')
                f.write(f'del /F /Q "{current_exe}" 2>nul\n')
                f.write(f'if exist "{current_exe}" (\n')
                f.write(f'    echo Waiting for file to unlock...\n')
                f.write(f'    timeout /t 2 /nobreak > nul\n')
                f.write(f'    goto retry\n')
                f.write(f')\n')
                f.write(f'move /Y "{temp_exe}" "{current_exe}"\n')
                f.write(f'if not exist "{current_exe}" (\n')
                f.write(f'    echo ERROR: Update failed!\n')
                f.write(f'    pause\n')
                f.write(f'    exit\n')
                f.write(f')\n')
                f.write('echo.\n')
                f.write('echo Update successful!\n')
                f.write('echo Restarting application...\n')
                f.write('timeout /t 2 /nobreak\n')
                f.write(f'cd /d "{exe_dir}"\n')
                f.write(f'start "" "{current_exe}"\n')
                f.write(f'del "%~f0"\n')
            
            # Run batch script
            subprocess.Popen(['cmd', '/c', batch_script], 
                           cwd=exe_dir)
            
            return True
            
        except Exception as e:
            print(f"Error downloading/installing update: {e}")
            import traceback
            traceback.print_exc()
            return False
