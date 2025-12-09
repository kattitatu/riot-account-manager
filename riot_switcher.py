import os
import subprocess
import platform
import time
import shutil
from pathlib import Path
import logging
from datetime import datetime
import re

class RiotSwitcher:
    def __init__(self):
        self.system = platform.system()
        self.riot_client_path = self.find_riot_client()
        self.league_path = self.find_league_client()
        self.backup_dir = Path("account_backups")
        self.backup_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging for debugging"""
        log_file = Path("riot_switcher_debug.log")
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("="*50)
        self.logger.info("Riot Switcher initialized")
        self.logger.info(f"Riot Client Path: {self.riot_client_path}")
        self.logger.info(f"League Path: {self.league_path}")
    
    def find_riot_client(self):
        """Find Riot Client installation path"""
        if self.system == "Windows":
            possible_paths = [
                Path("C:/Riot Games/Riot Client/RiotClientServices.exe"),
                Path(os.path.expandvars("%PROGRAMFILES%/Riot Games/Riot Client/RiotClientServices.exe")),
                Path(os.path.expandvars("%PROGRAMFILES(X86)%/Riot Games/Riot Client/RiotClientServices.exe"))
            ]
            for path in possible_paths:
                if path.exists():
                    return str(path)
        return None
    
    def find_league_client(self):
        """Find League of Legends installation path"""
        if self.system == "Windows":
            possible_paths = [
                Path("C:/Riot Games/League of Legends/LeagueClient.exe"),
                Path(os.path.expandvars("%PROGRAMFILES%/Riot Games/League of Legends/LeagueClient.exe")),
                Path(os.path.expandvars("%PROGRAMFILES(X86)%/Riot Games/League of Legends/LeagueClient.exe"))
            ]
            for path in possible_paths:
                if path.exists():
                    return str(path)
        return None
    
    def get_riot_config_path(self):
        """Get Riot Client config path"""
        if self.system == "Windows":
            local_appdata = os.getenv('LOCALAPPDATA')
            return Path(local_appdata) / "Riot Games" / "Riot Client" / "Data"
        return None
    

    
    def switch_account(self, username):
        """Switch to a different Riot account by swapping config files"""
        self.logger.info(f"Starting account switch to: {username}")
        try:
            # Kill existing Riot Client processes
            self.logger.info("Killing Riot processes...")
            self.kill_riot_processes()
            
            # Wait for processes to fully terminate (with timeout)
            self.logger.info("Waiting for processes to close...")
            if not self.wait_for_processes_to_close(timeout=5):
                self.logger.error("Processes did not close within timeout")
                return False, "Could not close Riot Client. Please close it manually and try again."
            self.logger.info("All processes closed successfully")
            
            # Additional wait for file handles to release and system to stabilize
            self.logger.info("Waiting for file handles to release...")
            time.sleep(3)
            
            # Get config path
            config_path = self.get_riot_config_path()
            self.logger.info(f"Config path: {config_path}")
            if not config_path:
                self.logger.error("Config path not found")
                return False, "Could not find Riot Client config directory."
            
            # Backup current session
            self.logger.info("Backing up current session...")
            self.backup_current_session()
            
            # Restore saved session for this account
            account_backup = self.backup_dir / f"{username}_session"
            self.logger.info(f"Account backup path: {account_backup}")
            self.logger.info(f"Backup exists: {account_backup.exists()}")
            
            if account_backup.exists():
                self.logger.info("Restoring saved session...")
                self.restore_session(account_backup)
                message = f"Switched to {username}. Launching Riot Client..."
            else:
                # First time using this account
                self.logger.info("First time login - clearing credentials...")
                self.clear_credentials()
                message = f"First time login for {username}. Please login manually.\nYour session will be saved for next time."
            
            # Launch Riot Client without game arguments so user can choose
            if self.riot_client_path:
                try:
                    self.logger.info(f"Launching Riot Client: {self.riot_client_path}")
                    self.logger.info("Launching without game arguments - user can choose game")
                    
                    # Launch without arguments
                    subprocess.Popen([self.riot_client_path])
                    time.sleep(2)
                    
                    # Verify it launched
                    is_running = self.is_riot_client_running()
                    self.logger.info(f"Riot Client running: {is_running}")
                    
                    if not is_running:
                        self.logger.error("Riot Client failed to launch")
                        return False, "Riot Client failed to launch. Please launch it manually."
                    
                    message = f"Switched to {username}. Riot Client is launching..."
                    self.logger.info("Account switch completed successfully")
                    return True, message
                    
                except Exception as e:
                    self.logger.error(f"Exception during launch: {e}", exc_info=True)
                    return False, f"Failed to launch Riot Client: {str(e)}"
            else:
                self.logger.error("Riot Client path not found")
                return False, "Riot Client not found. Please install it first."
        except Exception as e:
            self.logger.error(f"Exception during account switch: {e}", exc_info=True)
            return False, f"Error switching account: {str(e)}"
    
    def backup_current_session(self):
        """Backup current Riot session"""
        config_path = self.get_riot_config_path()
        if config_path and config_path.exists():
            backup_path = self.backup_dir / "last_session"
            if backup_path.exists():
                shutil.rmtree(backup_path, ignore_errors=True)
            try:
                shutil.copytree(config_path, backup_path)
            except Exception as e:
                print(f"Warning: Could not backup session: {e}")
    
    def restore_session(self, session_path):
        """Restore a saved session"""
        config_path = self.get_riot_config_path()
        if config_path and session_path.exists():
            self.logger.info(f"Restoring session from: {session_path}")
            self.logger.info(f"To config path: {config_path}")
            
            # Clear current config
            if config_path.exists():
                self.logger.info("Clearing current config...")
                cleared_count = 0
                for item in config_path.iterdir():
                    try:
                        if item.is_file():
                            item.unlink()
                            cleared_count += 1
                        elif item.is_dir():
                            shutil.rmtree(item)
                            cleared_count += 1
                    except Exception as e:
                        self.logger.warning(f"Could not clear {item.name}: {e}")
                self.logger.info(f"Cleared {cleared_count} items")
            
            # Copy saved session
            self.logger.info("Copying saved session files...")
            copied_count = 0
            failed_count = 0
            for item in session_path.iterdir():
                try:
                    if item.is_file():
                        shutil.copy2(item, config_path / item.name)
                        copied_count += 1
                        self.logger.debug(f"Copied file: {item.name}")
                    elif item.is_dir():
                        shutil.copytree(item, config_path / item.name)
                        copied_count += 1
                        self.logger.debug(f"Copied dir: {item.name}")
                except Exception as e:
                    failed_count += 1
                    self.logger.warning(f"Failed to copy {item.name}: {e}")
            
            self.logger.info(f"Session restore complete: {copied_count} copied, {failed_count} failed")
    
    def save_session_for_account(self, username):
        """Save current session for a specific account"""
        config_path = self.get_riot_config_path()
        if config_path and config_path.exists():
            account_backup = self.backup_dir / f"{username}_session"
            if account_backup.exists():
                shutil.rmtree(account_backup, ignore_errors=True)
            try:
                shutil.copytree(config_path, account_backup)
                self.logger.info(f"Session saved for {username}")
            except Exception as e:
                raise Exception(f"Could not save session: {e}")
    

    
    def kill_riot_processes(self):
        """Kill all Riot-related processes"""
        if self.system == "Windows":
            processes = [
                "RiotClientServices.exe",
                "RiotClientUx.exe",
                "RiotClientCrashHandler.exe",
                "LeagueClient.exe",
                "LeagueClientUx.exe",
                "LeagueClientUxRender.exe"
            ]
            
            # Kill processes twice to ensure they're really dead
            for attempt in range(2):
                self.logger.info(f"Kill attempt {attempt + 1}/2")
                for process in processes:
                    try:
                        result = subprocess.run(["taskkill", "/F", "/IM", process], 
                                     capture_output=True, check=False, text=True)
                        if result.returncode == 0:
                            self.logger.info(f"Killed process: {process}")
                    except Exception as e:
                        self.logger.debug(f"Could not kill {process}: {e}")
                
                if attempt == 0:
                    time.sleep(1)  # Wait between attempts
    
    def wait_for_processes_to_close(self, timeout=10):
        """Wait for Riot processes to fully close"""
        if self.system == "Windows":
            processes = [
                "RiotClientServices.exe",
                "RiotClientUx.exe",
                "LeagueClient.exe",
                "LeagueClientUx.exe"
            ]
            
            self.logger.info(f"Waiting up to {timeout} seconds for processes to close...")
            start_time = time.time()
            while time.time() - start_time < timeout:
                # Check if any processes are still running
                still_running = []
                for process in processes:
                    try:
                        result = subprocess.run(["tasklist", "/FI", f"IMAGENAME eq {process}"], 
                                              capture_output=True, text=True, check=False)
                        if process in result.stdout:
                            still_running.append(process)
                    except:
                        pass
                
                if not still_running:
                    elapsed = time.time() - start_time
                    self.logger.info(f"All processes closed after {elapsed:.1f} seconds")
                    return True
                
                if len(still_running) > 0:
                    self.logger.debug(f"Still running: {', '.join(still_running)}")
                
                time.sleep(0.5)
            
            self.logger.error(f"Timeout: Processes still running after {timeout} seconds: {', '.join(still_running)}")
            return False
        return True
    
    def is_riot_client_running(self):
        """Check if Riot Client is running"""
        if self.system == "Windows":
            try:
                result = subprocess.run(["tasklist", "/FI", "IMAGENAME eq RiotClientServices.exe"], 
                                      capture_output=True, text=True, check=False)
                return "RiotClientServices.exe" in result.stdout
            except:
                return False
        return False
    
    def is_league_client_running(self):
        """Check if League Client is running"""
        if self.system == "Windows":
            try:
                result = subprocess.run(["tasklist", "/FI", "IMAGENAME eq LeagueClient.exe"], 
                                      capture_output=True, text=True, check=False)
                return "LeagueClient.exe" in result.stdout
            except:
                return False
        return False
    
    def show_riot_client_window(self):
        """Bring Riot Client window to foreground"""
        if self.system == "Windows":
            try:
                # Use PowerShell to find and activate the Riot Client window
                ps_script = """
                Add-Type @"
                    using System;
                    using System.Runtime.InteropServices;
                    public class Win32 {
                        [DllImport("user32.dll")]
                        public static extern bool SetForegroundWindow(IntPtr hWnd);
                        [DllImport("user32.dll")]
                        public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
                        [DllImport("user32.dll")]
                        public static extern bool IsIconic(IntPtr hWnd);
                    }
"@
                $process = Get-Process | Where-Object {$_.ProcessName -eq "RiotClientUx"}
                if ($process) {
                    $hwnd = $process.MainWindowHandle
                    if ($hwnd -ne 0) {
                        if ([Win32]::IsIconic($hwnd)) {
                            [Win32]::ShowWindow($hwnd, 9) | Out-Null
                        }
                        [Win32]::SetForegroundWindow($hwnd) | Out-Null
                    }
                }
                """
                subprocess.run(["powershell", "-Command", ps_script], 
                             capture_output=True, check=False, timeout=5)
                self.logger.info("Attempted to show Riot Client window")
            except Exception as e:
                self.logger.error(f"Failed to show Riot Client window: {e}")
    
    def clear_credentials(self):
        """Clear saved Riot credentials"""
        config_path = self.get_riot_config_path()
        if config_path and config_path.exists():
            # Clear RiotGamesPrivateSettings.yaml and other session files
            files_to_clear = [
                "RiotGamesPrivateSettings.yaml",
                "RiotGamesPrivateSettings.yaml.bak"
            ]
            for filename in files_to_clear:
                file_path = config_path / filename
                if file_path.exists():
                    try:
                        file_path.unlink()
                    except:
                        pass
