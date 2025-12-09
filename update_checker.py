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
            # Get the actual exe location
            # For --onefile, we need the ORIGINAL exe location, not the temp extraction
            if getattr(sys, 'frozen', False):
                # Use sys.argv[0] which points to the actual exe location
                current_exe = os.path.abspath(sys.argv[0])
            else:
                # Running as script
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
            
            # Create robust update script with process termination
            current_exe_win = current_exe.replace('/', '\\')
            temp_exe_win = temp_exe.replace('/', '\\')
            exe_dir_win = exe_dir.replace('/', '\\')
            exe_name = os.path.basename(current_exe)
            
            update_script = os.path.join(exe_dir, "update.bat")
            with open(update_script, 'w') as f:
                f.write('@echo off\n')
                f.write(f'cd /d "{exe_dir_win}"\n')
                f.write('\n')
                f.write('REM Wait for app to close\n')
                f.write('timeout /t 2 /nobreak > nul\n')
                f.write('\n')
                f.write('REM Force kill any remaining processes\n')
                f.write(f'taskkill /F /IM "{exe_name}" 2>nul\n')
                f.write('timeout /t 1 /nobreak > nul\n')
                f.write('\n')
                f.write('REM Delete old exe with retry\n')
                f.write(':retry_delete\n')
                f.write(f'del /F /Q "{current_exe_win}" 2>nul\n')
                f.write(f'if exist "{current_exe_win}" (\n')
                f.write('    timeout /t 1 /nobreak > nul\n')
                f.write('    goto retry_delete\n')
                f.write(')\n')
                f.write('\n')
                f.write('REM Move new exe to replace old one\n')
                f.write(f'move /Y "{temp_exe_win}" "{current_exe_win}"\n')
                f.write('\n')
                f.write('REM Verify the move succeeded\n')
                f.write(f'if not exist "{current_exe_win}" (\n')
                f.write('    echo Update failed!\n')
                f.write('    pause\n')
                f.write('    exit /b 1\n')
                f.write(')\n')
                f.write('\n')
                f.write('REM Wait a moment then relaunch\n')
                f.write('timeout /t 1 /nobreak > nul\n')
                f.write(f'start "" "{current_exe_win}"\n')
                f.write('\n')
                f.write('REM Clean up this script\n')
                f.write('del "%~f0"\n')
            
            # Run update script detached
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            subprocess.Popen(
                ['cmd', '/c', update_script],
                cwd=exe_dir,
                creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS,
                startupinfo=startupinfo,
                close_fds=True,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            return True
            
        except Exception as e:
            print(f"Error downloading/installing update: {e}")
            import traceback
            traceback.print_exc()
            return False
