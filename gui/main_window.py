import tkinter as tk
from tkinter import ttk, messagebox
from gui.account_card import AccountCard
from gui.add_account_dialog import AddAccountDialog
from gui.edit_account_dialog import EditAccountDialog
from gui.settings_dialog import SettingsDialog
from gui.ranked_stats_dialog import RankedStatsDialog
from gui.live_game_display import LiveGameDisplay
from gui.update_dialog import UpdateDialog
from riot_switcher import RiotSwitcher
from rank_fetcher import RankFetcher
from rank_icons import RankIcons
from profile_icon_fetcher import ProfileIconFetcher
from status_fetcher import StatusFetcher
from live_game_fetcher import LiveGameFetcher
from update_checker import UpdateChecker
from version import __version__
import threading
import os
from config import get_api_key, get_region

class MainWindow:
    def __init__(self, root, account_manager):
        self.root = root
        self.account_manager = account_manager
        self.riot_switcher = RiotSwitcher()
        api_key = get_api_key()
        self.rank_fetcher = RankFetcher(api_key=api_key)
        self.profile_icon_fetcher = ProfileIconFetcher(api_key=api_key)
        self.status_fetcher = StatusFetcher(api_key=api_key)
        self.live_game_fetcher = LiveGameFetcher(api_key=api_key)
        self.rank_icons = RankIcons()
        self.account_cards = []
        self.status_label = None
        self.status_update_job = None
        
        # Update checker
        self.update_checker = UpdateChecker("kattitatu/riot-account-manager")
        
        self.setup_window_icon()
        self.setup_ui()
        self.refresh_accounts()
        self.update_status()  # Initial status fetch
        self.schedule_status_update()  # Schedule periodic updates
        self.check_for_updates()  # Check for updates on startup
    
    def setup_window_icon(self):
        """Setup the window icon"""
        try:
            icon_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'rose.ico')
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception as e:
            print(f"Could not load icon: {e}")
    
    def setup_ui(self):
        """Setup the main UI"""
        # Top bar with buttons - reduced height
        top_frame = tk.Frame(self.root, bg="#2c2c2c", height=45)
        top_frame.pack(fill=tk.X, side=tk.TOP)
        top_frame.pack_propagate(False)
        
        # Status indicator on the left
        self.status_label = tk.Label(top_frame, text="● Loading...", 
                                     font=("Arial", 9, "bold"), bg="#2c2c2c", fg="#888888")
        self.status_label.pack(side=tk.LEFT, padx=15, pady=10)
        
        # Version number
        version_label = tk.Label(top_frame, text=f"v{__version__}", 
                                font=("Arial", 8), bg="#2c2c2c", fg="#666666")
        version_label.pack(side=tk.LEFT, padx=(0, 15), pady=10)
        
        # Right side buttons
        settings_btn = tk.Button(top_frame, text="⚙️ Settings", 
                           command=self.open_settings,
                           bg="#6c757d", fg="white", font=("Arial", 9),
                           padx=12, pady=4, relief=tk.FLAT, cursor="hand2")
        settings_btn.pack(side=tk.RIGHT, padx=(5, 15), pady=10)
        
        # Tab control
        tab_container = tk.Frame(self.root, bg="#1e1e1e")
        tab_container.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook (tab control)
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook', background='#1e1e1e', borderwidth=0)
        style.configure('TNotebook.Tab', background='#2d2d2d', foreground='white', 
                       padding=[20, 10], font=('Arial', 10), focuscolor='none')
        style.map('TNotebook.Tab', background=[('selected', '#0078d4')], 
                 foreground=[('selected', 'white')],
                 focuscolor=[('selected', 'none')])
        
        self.notebook = ttk.Notebook(tab_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Accounts Tab
        self.accounts_tab = tk.Frame(self.notebook, bg="#1e1e1e")
        self.notebook.add(self.accounts_tab, text="Accounts")
        
        # Setup accounts tab content
        self.setup_accounts_tab()
        
        # Live Game Tab
        self.live_game_tab = tk.Frame(self.notebook, bg="#1e1e1e")
        self.notebook.add(self.live_game_tab, text="Live Game")
        
        # Setup live game tab content
        self.setup_live_game_tab()
    
    def setup_accounts_tab(self):
        """Setup the accounts tab with buttons and account grid"""
        # Buttons frame at top of accounts tab - reduced height
        btn_frame = tk.Frame(self.accounts_tab, bg="#2c2c2c", height=45)
        btn_frame.pack(fill=tk.X, side=tk.TOP)
        btn_frame.pack_propagate(False)
        
        add_btn = tk.Button(btn_frame, text="+ Add Account", 
                           command=self.add_account,
                           bg="#0078d4", fg="white", font=("Arial", 9),
                           padx=12, pady=4, relief=tk.FLAT, cursor="hand2")
        add_btn.pack(side=tk.RIGHT, padx=(5, 15), pady=10)
        
        save_session_btn = tk.Button(btn_frame, text="💾 Save Current Session", 
                           command=self.save_current_session,
                           bg="#28a745", fg="white", font=("Arial", 9),
                           padx=12, pady=4, relief=tk.FLAT, cursor="hand2")
        save_session_btn.pack(side=tk.RIGHT, padx=5, pady=10)
        
        refresh_all_btn = tk.Button(btn_frame, text="🔄 Refresh All", 
                           command=self.refresh_all_accounts,
                           bg="#17a2b8", fg="white", font=("Arial", 9),
                           padx=12, pady=4, relief=tk.FLAT, cursor="hand2")
        refresh_all_btn.pack(side=tk.RIGHT, padx=5, pady=10)
        
        # Frame for account grid with canvas for scrolling (no scrollbar)
        container = tk.Frame(self.accounts_tab, bg="#1e1e1e")
        container.pack(fill=tk.BOTH, expand=True)
        
        self.accounts_canvas = tk.Canvas(container, bg="#1e1e1e", highlightthickness=0)
        self.scrollable_frame = tk.Frame(self.accounts_canvas, bg="#1e1e1e")
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.accounts_canvas.configure(scrollregion=self.accounts_canvas.bbox("all"))
        )
        
        self.accounts_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.accounts_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Mouse wheel scrolling (no scrollbar visible)
        def on_mousewheel(event):
            self.accounts_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        self.accounts_canvas.bind_all("<MouseWheel>", on_mousewheel)
    
    def setup_live_game_tab(self):
        """Setup the live game tab with account selector and refresh"""
        # Top control bar - reduced height
        control_frame = tk.Frame(self.live_game_tab, bg="#2c2c2c", height=45)
        control_frame.pack(fill=tk.X, side=tk.TOP)
        control_frame.pack_propagate(False)
        
        # Account selector label
        selector_label = tk.Label(control_frame, text="Account:", 
                                 font=("Arial", 9, "bold"), bg="#2c2c2c", fg="white")
        selector_label.pack(side=tk.LEFT, padx=(15, 8), pady=10)
        
        # Account dropdown
        self.live_game_account_var = tk.StringVar()
        self.live_game_account_combo = ttk.Combobox(control_frame, 
                                                    textvariable=self.live_game_account_var,
                                                    state="readonly",
                                                    font=("Arial", 9),
                                                    width=25)
        self.live_game_account_combo.pack(side=tk.LEFT, padx=5, pady=10)
        
        # Populate dropdown with accounts
        self.update_live_game_accounts()
        
        # Refresh button
        refresh_btn = tk.Button(control_frame, text="🔄 Refresh", 
                               command=self.refresh_live_game,
                               bg="#0078d4", fg="white", font=("Arial", 9),
                               padx=12, pady=4, relief=tk.FLAT, cursor="hand2")
        refresh_btn.pack(side=tk.LEFT, padx=8, pady=10)
        
        # Test button (for dummy data)
        test_btn = tk.Button(control_frame, text="🧪 Test with Dummy Data", 
                            command=self.show_dummy_live_game,
                            bg="#6c757d", fg="white", font=("Arial", 9),
                            padx=12, pady=4, relief=tk.FLAT, cursor="hand2")
        test_btn.pack(side=tk.LEFT, padx=5, pady=10)
        
        # Content area (no scrollbar)
        self.live_game_content = tk.Frame(self.live_game_tab, bg="#1e1e1e")
        self.live_game_content.pack(fill=tk.BOTH, expand=True)
        
        # Initial placeholder
        self.show_live_game_placeholder()
    
    def update_live_game_accounts(self):
        """Update the account dropdown in live game tab"""
        accounts = self.account_manager.get_all_accounts()
        
        if not accounts:
            self.live_game_account_combo['values'] = ["No accounts available"]
            self.live_game_account_combo.current(0)
            return
        
        # Create list of account display names
        account_names = [acc.get('display_name', acc.get('username', 'Unknown')) for acc in accounts]
        self.live_game_account_combo['values'] = account_names
        
        # Select first account by default
        if account_names:
            self.live_game_account_combo.current(0)
    
    def show_live_game_placeholder(self):
        """Show placeholder message in live game content area"""
        # Clear existing content
        for widget in self.live_game_content.winfo_children():
            widget.destroy()
        
        placeholder = tk.Label(self.live_game_content, 
                              text="Select an account and click Refresh\nto view live game data", 
                              font=("Arial", 14), bg="#1e1e1e", fg="#888888")
        placeholder.pack(expand=True, pady=100)
    
    def refresh_live_game(self):
        """Refresh live game data for selected account"""
        selected_name = self.live_game_account_var.get()
        
        if not selected_name or selected_name == "No accounts available":
            messagebox.showwarning("No Account", "Please select an account first.")
            return
        
        # Find the selected account
        accounts = self.account_manager.get_all_accounts()
        selected_account = None
        
        for acc in accounts:
            if acc.get('display_name', acc.get('username')) == selected_name:
                selected_account = acc
                break
        
        if not selected_account:
            messagebox.showerror("Error", "Selected account not found.")
            return
        
        # Check if account has Riot ID
        riot_id = selected_account.get('riot_id', '')
        if not riot_id:
            messagebox.showwarning("No Riot ID", 
                                  f"Account '{selected_name}' doesn't have a Riot ID set.\nPlease edit the account and add a Riot ID (e.g. Name#TAG).")
            return
        
        # Show loading message
        for widget in self.live_game_content.winfo_children():
            widget.destroy()
        
        loading_label = tk.Label(self.live_game_content, 
                                text=f"Fetching live game data for {selected_name}...", 
                                font=("Arial", 12), bg="#1e1e1e", fg="white")
        loading_label.pack(expand=True, pady=100)
        
        # Fetch live game data in background thread
        def fetch_in_thread():
            region = get_region()
            game_data, error = self.live_game_fetcher.fetch_live_game(riot_id, region)
            
            # Update UI in main thread
            self.root.after(0, lambda: self._handle_live_game_result(selected_name, game_data, error))
        
        thread = threading.Thread(target=fetch_in_thread, daemon=True)
        thread.start()
    
    def refresh_accounts(self):
        """Refresh the account grid"""
        # Clear existing cards
        for card in self.account_cards:
            card.destroy()
        self.account_cards.clear()
        
        # Get all accounts
        accounts = self.account_manager.get_all_accounts()
        
        if not accounts:
            return
        
        # Determine optimal number of columns based on account count
        num_accounts = len(accounts)
        if num_accounts == 1:
            columns = 1
        elif num_accounts == 2:
            columns = 2
        elif num_accounts == 3:
            columns = 3
        else:
            columns = 4
        
        # Create grid of account cards
        for idx, account in enumerate(accounts):
            row = idx // columns
            col = idx % columns
            
            card = AccountCard(
                self.scrollable_frame,
                account,
                on_switch=lambda acc=account: self.switch_account(acc),
                on_edit=lambda acc=account: self.edit_account(acc),
                on_delete=lambda acc=account: self.delete_account(acc),
                on_save_session=lambda acc=account: self.save_session_for_account(acc),
                on_refresh_rank=lambda acc=account: self.refresh_rank(acc),
                on_show_stats=lambda acc=account: self.show_ranked_stats(acc),
                is_active=False,
                rank_icons=self.rank_icons,
                profile_icon_fetcher=self.profile_icon_fetcher
            )
            card.grid(row=row, column=col, padx=10, pady=10, sticky="ew")
            self.account_cards.append(card)
        
        # Configure grid weights for equal distribution
        for i in range(columns):
            self.scrollable_frame.grid_columnconfigure(i, weight=1, uniform="col")
        
        # Update live game account dropdown
        if hasattr(self, 'live_game_account_combo'):
            self.update_live_game_accounts()
    
    def open_settings(self):
        """Open settings dialog"""
        dialog = SettingsDialog(self.root)
        self.root.wait_window(dialog.dialog)
        # Reload API key and fetchers in case settings changed
        api_key = get_api_key()
        self.rank_fetcher = RankFetcher(api_key=api_key)
        self.status_fetcher = StatusFetcher(api_key=api_key)
        self.live_game_fetcher = LiveGameFetcher(api_key=api_key)
        # Refresh status with new settings
        self.update_status()
    
    def add_account(self):
        """Open add account dialog"""
        dialog = AddAccountDialog(self.root, self.account_manager)
        self.root.wait_window(dialog.dialog)
        self.refresh_accounts()
    
    def edit_account(self, account):
        """Open edit account dialog"""
        dialog = EditAccountDialog(self.root, self.account_manager, account)
        self.root.wait_window(dialog.dialog)
        self.refresh_accounts()
    
    def delete_account(self, account):
        """Delete an account"""
        if messagebox.askyesno("Confirm Delete", 
                              f"Are you sure you want to delete '{account['display_name']}'?"):
            self.account_manager.delete_account(account["id"])
            self.refresh_accounts()
    
    def show_ranked_stats(self, account):
        """Show ranked stats dialog"""
        dialog = RankedStatsDialog(self.root, account)
        self.root.wait_window(dialog.dialog)
    

    
    def refresh_all_accounts(self):
        """Refresh data for all accounts"""
        accounts = self.account_manager.get_all_accounts()
        if not accounts:
            messagebox.showinfo("No Accounts", "No accounts to refresh.")
            return
        
        # Show progress dialog
        progress_dialog = tk.Toplevel(self.root)
        progress_dialog.title("Refreshing All Accounts")
        progress_dialog.geometry("400x150")
        progress_dialog.configure(bg="#2d2d2d")
        progress_dialog.transient(self.root)
        progress_dialog.grab_set()
        
        progress_label = tk.Label(progress_dialog, text="Starting refresh...", 
                                 font=("Arial", 10), bg="#2d2d2d", fg="white")
        progress_label.pack(pady=30)
        
        status_label = tk.Label(progress_dialog, text="", 
                               font=("Arial", 9), bg="#2d2d2d", fg="#aaaaaa")
        status_label.pack(pady=10)
        
        def refresh_all_in_thread():
            total = len(accounts)
            for idx, account in enumerate(accounts):
                riot_id = account.get('riot_id')
                if not riot_id:
                    continue
                
                # Update progress
                self.root.after(0, lambda i=idx, name=account['display_name']: 
                               progress_label.config(text=f"Refreshing {i+1}/{total}...") or
                               status_label.config(text=f"Fetching data for {name}"))
                
                # Fetch data
                rank, error, ranked_stats = self.rank_fetcher.fetch_rank(riot_id)
                profile_icon_id, summoner_level = self.profile_icon_fetcher.fetch_profile_data(riot_id)
                
                # Update account
                updates = {}
                if rank and not error:
                    updates['rank'] = rank
                if profile_icon_id:
                    updates['profile_icon_id'] = profile_icon_id
                if summoner_level is not None:
                    updates['summoner_level'] = summoner_level
                if ranked_stats:
                    updates['ranked_stats'] = ranked_stats
                
                if updates:
                    self.account_manager.update_account(account["id"], **updates)
            
            # Close dialog and refresh UI
            self.root.after(0, lambda: progress_dialog.destroy())
            self.root.after(0, lambda: self.refresh_accounts())
            self.root.after(0, lambda: messagebox.showinfo("Success", f"Refreshed {total} accounts!"))
        
        # Start in background thread
        thread = threading.Thread(target=refresh_all_in_thread, daemon=True)
        thread.start()
    
    def switch_account(self, account):
        """Switch to selected account"""
        success, message = self.riot_switcher.switch_account(
            account["username"]
        )
        
        # Only show error messages, not success
        if not success:
            messagebox.showerror("Error", message)
    
    def save_session_for_account(self, account):
        """Save current Riot session for an account"""
        try:
            self.riot_switcher.save_session_for_account(account["username"])
            # Session saved silently, no popup
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save session: {str(e)}")
    
    def save_current_session(self):
        """Save current session - ask which account it belongs to"""
        accounts = self.account_manager.get_all_accounts()
        if not accounts:
            messagebox.showwarning("No Accounts", "Please add an account first.")
            return
        
        # Create a simple dialog to select account
        dialog = tk.Toplevel(self.root)
        dialog.title("Save Session For...")
        dialog.geometry("300x400")
        dialog.configure(bg="#2d2d2d")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Select Account:", font=("Arial", 12, "bold"),
                bg="#2d2d2d", fg="white").pack(pady=20)
        
        listbox = tk.Listbox(dialog, font=("Arial", 10), bg="#1e1e1e", fg="white",
                            selectbackground="#0078d4", relief=tk.FLAT)
        listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))
        
        for account in accounts:
            listbox.insert(tk.END, account["display_name"])
        
        def save_selected():
            selection = listbox.curselection()
            if selection:
                account = accounts[selection[0]]
                self.riot_switcher.save_session_for_account(account["username"])
                # Session saved silently, no popup
                dialog.destroy()
            else:
                messagebox.showwarning("No Selection", "Please select an account.")
        
        tk.Button(dialog, text="Save Session", command=save_selected,
                 bg="#0078d4", fg="white", font=("Arial", 10, "bold"),
                 padx=20, pady=8, relief=tk.FLAT, cursor="hand2").pack(pady=(0, 20))
    
    def refresh_rank(self, account):
        """Refresh rank and profile icon for an account"""
        riot_id = account.get("riot_id", "")
        
        if not riot_id:
            messagebox.showwarning("No Riot ID", 
                                  "Please add a Riot ID (e.g. Name#TAG) in the account settings to fetch data.")
            return
        
        # Show loading message
        loading_dialog = tk.Toplevel(self.root)
        loading_dialog.title("Fetching Data...")
        loading_dialog.geometry("300x100")
        loading_dialog.configure(bg="#2d2d2d")
        loading_dialog.transient(self.root)
        loading_dialog.grab_set()
        
        tk.Label(loading_dialog, text=f"Fetching data for {riot_id}...", 
                font=("Arial", 10), bg="#2d2d2d", fg="white").pack(pady=30)
        
        def fetch_in_thread():
            # Fetch rank and stats
            rank, error, ranked_stats = self.rank_fetcher.fetch_rank(riot_id)
            
            # Fetch profile icon and summoner level
            profile_icon_id, summoner_level = self.profile_icon_fetcher.fetch_profile_data(riot_id)
            
            # Update UI in main thread
            self.root.after(0, lambda: self._handle_rank_result(account, rank, error, profile_icon_id, summoner_level, ranked_stats, loading_dialog))
        
        # Start fetching in background thread
        thread = threading.Thread(target=fetch_in_thread, daemon=True)
        thread.start()
    
    def _handle_rank_result(self, account, rank, error, profile_icon_id, summoner_level, ranked_stats, loading_dialog):
        """Handle the rank, profile icon, summoner level, and ranked stats fetch result"""
        loading_dialog.destroy()
        
        updates = {}
        messages = []
        
        if rank and not error:
            updates['rank'] = rank
            messages.append(f"Rank: {rank}")
        
        if profile_icon_id:
            updates['profile_icon_id'] = profile_icon_id
            messages.append(f"Profile Icon: {profile_icon_id}")
        
        if summoner_level is not None:
            updates['summoner_level'] = summoner_level
            messages.append(f"Level: {summoner_level}")
        
        if ranked_stats:
            updates['ranked_stats'] = ranked_stats
            messages.append(f"W/L: {ranked_stats.get('wins', 0)}/{ranked_stats.get('losses', 0)}")
        
        if updates:
            self.account_manager.update_account(account["id"], **updates)
            # Refresh silently, no popup
            self.refresh_accounts()
        elif error:
            messagebox.showerror("Error", error)
        else:
            messagebox.showwarning("Not Found", "Could not find data for this account.")

    def update_status(self):
        """Update server status display"""
        def fetch_status():
            region = get_region()
            status, incidents, maintenances = self.status_fetcher.fetch_status(region)
            region_name = self.status_fetcher.get_region_name(region)
            
            # Update UI in main thread
            self.root.after(0, lambda: self._update_status_display(region_name, status, incidents, maintenances))
        
        # Fetch in background thread
        thread = threading.Thread(target=fetch_status, daemon=True)
        thread.start()
    
    def _update_status_display(self, region_name, status, incidents, maintenances):
        """Update the status label with fetched data"""
        if not self.status_label:
            return
        
        # Status colors and symbols
        status_config = {
            'online': {'symbol': '●', 'color': '#28a745', 'text': 'Online'},
            'degraded': {'symbol': '●', 'color': '#ffc107', 'text': 'Degraded'},
            'offline': {'symbol': '●', 'color': '#dc3545', 'text': 'Offline'},
            'unknown': {'symbol': '●', 'color': '#888888', 'text': 'Unknown'}
        }
        
        config = status_config.get(status, status_config['unknown'])
        
        # Build status text
        status_text = f"{config['symbol']} {region_name}: {config['text']}"
        
        # Add incident/maintenance count if any
        total_issues = len(incidents) + len(maintenances)
        if total_issues > 0:
            status_text += f" ({total_issues})"
        
        self.status_label.config(text=status_text, fg=config['color'])
        
        # Make status clickable to show details
        self.status_label.bind("<Button-1>", lambda e: self.show_status_details(region_name, status, incidents, maintenances))
        self.status_label.config(cursor="hand2")
    
    def show_status_details(self, region_name, status, incidents, maintenances):
        """Show detailed status information in a dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"{region_name} Server Status")
        dialog.geometry("500x400")
        dialog.configure(bg="#2d2d2d")
        dialog.transient(self.root)
        
        # Title
        title_frame = tk.Frame(dialog, bg="#2d2d2d")
        title_frame.pack(fill=tk.X, padx=20, pady=20)
        
        status_colors = {
            'online': '#28a745',
            'degraded': '#ffc107',
            'offline': '#dc3545',
            'unknown': '#888888'
        }
        
        title = tk.Label(title_frame, text=f"{region_name} - {status.upper()}", 
                        font=("Arial", 14, "bold"), bg="#2d2d2d", 
                        fg=status_colors.get(status, '#888888'))
        title.pack()
        
        # Scrollable content
        canvas = tk.Canvas(dialog, bg="#2d2d2d", highlightthickness=0)
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        content_frame = tk.Frame(canvas, bg="#2d2d2d")
        
        content_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=content_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Display incidents
        if incidents:
            incidents_label = tk.Label(content_frame, text="Active Incidents:", 
                                      font=("Arial", 12, "bold"), bg="#2d2d2d", fg="white")
            incidents_label.pack(anchor="w", pady=(10, 5))
            
            for incident in incidents:
                self._add_issue_to_frame(content_frame, incident, is_maintenance=False)
        
        # Display maintenances
        if maintenances:
            maint_label = tk.Label(content_frame, text="Scheduled Maintenances:", 
                                  font=("Arial", 12, "bold"), bg="#2d2d2d", fg="white")
            maint_label.pack(anchor="w", pady=(10, 5))
            
            for maintenance in maintenances:
                self._add_issue_to_frame(content_frame, maintenance, is_maintenance=True)
        
        # If no issues
        if not incidents and not maintenances:
            no_issues = tk.Label(content_frame, text="No active incidents or maintenances", 
                                font=("Arial", 10), bg="#2d2d2d", fg="#888888")
            no_issues.pack(pady=20)
        
        # Close button
        close_btn = tk.Button(dialog, text="Close", command=dialog.destroy,
                             bg="#4a4a4a", fg="white", font=("Arial", 10),
                             padx=20, pady=8, relief=tk.FLAT, cursor="hand2")
        close_btn.pack(pady=20)
    
    def _add_issue_to_frame(self, parent, issue, is_maintenance):
        """Add an incident or maintenance to the details frame"""
        issue_frame = tk.Frame(parent, bg="#1e1e1e", relief=tk.RAISED, borderwidth=1)
        issue_frame.pack(fill=tk.X, pady=5, padx=5)
        
        # Get title (prefer English)
        titles = issue.get('titles', [])
        title = "Unknown Issue"
        for title_obj in titles:
            if title_obj.get('locale') == 'en_US':
                title = title_obj.get('content', title)
                break
        
        # Title
        title_label = tk.Label(issue_frame, text=title, 
                              font=("Arial", 10, "bold"), bg="#1e1e1e", fg="white",
                              wraplength=450, justify=tk.LEFT)
        title_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Severity or status
        if is_maintenance:
            status = issue.get('maintenance_status', 'unknown')
            status_label = tk.Label(issue_frame, text=f"Status: {status}", 
                                   font=("Arial", 9), bg="#1e1e1e", fg="#ffc107")
            status_label.pack(anchor="w", padx=10, pady=(0, 5))
        else:
            severity = issue.get('incident_severity', 'info')
            severity_colors = {'critical': '#dc3545', 'warning': '#ffc107', 'info': '#17a2b8'}
            severity_label = tk.Label(issue_frame, text=f"Severity: {severity.upper()}", 
                                     font=("Arial", 9), bg="#1e1e1e", 
                                     fg=severity_colors.get(severity, '#888888'))
            severity_label.pack(anchor="w", padx=10, pady=(0, 5))
        
        # Latest update
        updates = issue.get('updates', [])
        if updates:
            latest_update = updates[0]
            translations = latest_update.get('translations', [])
            update_text = "No details available"
            for trans in translations:
                if trans.get('locale') == 'en_US':
                    update_text = trans.get('content', update_text)
                    break
            
            update_label = tk.Label(issue_frame, text=update_text, 
                                   font=("Arial", 9), bg="#1e1e1e", fg="#aaaaaa",
                                   wraplength=450, justify=tk.LEFT)
            update_label.pack(anchor="w", padx=10, pady=(0, 10))
    
    def schedule_status_update(self):
        """Schedule periodic status updates every 10 minutes"""
        # Cancel existing job if any
        if self.status_update_job:
            self.root.after_cancel(self.status_update_job)
        
        # Schedule next update in 10 minutes (600000 ms)
        self.status_update_job = self.root.after(600000, self._periodic_status_update)
    
    def _periodic_status_update(self):
        """Periodic status update callback"""
        self.update_status()
        self.schedule_status_update()

    def show_no_live_game(self, account_name):
        """Show message when account is not in a live game"""
        # Clear existing content
        for widget in self.live_game_content.winfo_children():
            widget.destroy()
        
        no_game_label = tk.Label(self.live_game_content, 
                                text=f"{account_name} is not currently in a game", 
                                font=("Arial", 14), bg="#1e1e1e", fg="#888888")
        no_game_label.pack(expand=True, pady=100)
    
    def _handle_live_game_result(self, account_name, game_data, error):
        """Handle the live game fetch result"""
        # Clear loading message
        for widget in self.live_game_content.winfo_children():
            widget.destroy()
        
        if error:
            # Show error message
            error_label = tk.Label(self.live_game_content, 
                                  text=f"Error: {error}", 
                                  font=("Arial", 12), bg="#1e1e1e", fg="#dc3545")
            error_label.pack(expand=True, pady=100)
        elif not game_data:
            # Not in game
            self.show_no_live_game(account_name)
        else:
            # Display live game data
            LiveGameDisplay(self.live_game_content, game_data, self.rank_icons)

    def show_dummy_live_game(self):
        """Show dummy live game data for testing"""
        # Create realistic dummy game data
        dummy_data = {
            'gameQueueConfigId': 420,  # Ranked Solo/Duo
            'mapId': 11,  # Summoner's Rift
            'bannedChampions': [
                # Blue team bans
                {'championId': 157, 'teamId': 100, 'pickTurn': 1},  # Yasuo
                {'championId': 777, 'teamId': 100, 'pickTurn': 2},  # Yone
                {'championId': 555, 'teamId': 100, 'pickTurn': 3},  # Pyke
                {'championId': 350, 'teamId': 100, 'pickTurn': 4},  # Yuumi
                {'championId': 141, 'teamId': 100, 'pickTurn': 5},  # Kayn
                # Red team bans
                {'championId': 67, 'teamId': 200, 'pickTurn': 6},   # Vayne
                {'championId': 11, 'teamId': 200, 'pickTurn': 7},   # Master Yi
                {'championId': 107, 'teamId': 200, 'pickTurn': 8},  # Rengar
                {'championId': 245, 'teamId': 200, 'pickTurn': 9},  # Ekko
                {'championId': 84, 'teamId': 200, 'pickTurn': 10},  # Akali
            ],
            'participants': [
                # Blue Team
                {
                    'teamId': 100,
                    'championId': 86,  # Garen
                    'spell1Id': 4,  # Flash
                    'spell2Id': 14,  # Ignite
                    'riotId': 'TopLaner#EUW',
                    'puuid': 'dummy-puuid-1',
                    'rank_data': {'tier': 'GOLD', 'rank': 'II', 'lp': 45, 'wins': 120, 'losses': 110},
                    'mastery_points': 250000,
                    'summoner_level': 156,
                    'is_target': False
                },
                {
                    'teamId': 100,
                    'championId': 64,  # Lee Sin
                    'spell1Id': 4,  # Flash
                    'spell2Id': 11,  # Smite
                    'riotId': 'JungleMain#EUW',
                    'puuid': 'dummy-puuid-2',
                    'rank_data': {'tier': 'PLATINUM', 'rank': 'IV', 'lp': 78, 'wins': 200, 'losses': 180},
                    'mastery_points': 450000,
                    'summoner_level': 234,
                    'is_target': True
                },
                {
                    'teamId': 100,
                    'championId': 103,  # Ahri
                    'spell1Id': 4,  # Flash
                    'spell2Id': 14,  # Ignite
                    'riotId': 'MidOrFeed#EUW',
                    'puuid': 'dummy-puuid-3',
                    'rank_data': {'tier': 'GOLD', 'rank': 'I', 'lp': 92, 'wins': 145, 'losses': 130},
                    'mastery_points': 180000,
                    'summoner_level': 189,
                    'is_target': False
                },
                {
                    'teamId': 100,
                    'championId': 222,  # Jinx
                    'spell1Id': 4,  # Flash
                    'spell2Id': 7,  # Heal
                    'riotId': 'ADCPlayer#EUW',
                    'puuid': 'dummy-puuid-4',
                    'rank_data': {'tier': 'PLATINUM', 'rank': 'III', 'lp': 34, 'wins': 167, 'losses': 155},
                    'mastery_points': 320000,
                    'summoner_level': 201,
                    'is_target': False
                },
                {
                    'teamId': 100,
                    'championId': 412,  # Thresh
                    'spell1Id': 4,  # Flash
                    'spell2Id': 14,  # Ignite
                    'riotId': 'SupportGod#EUW',
                    'puuid': 'dummy-puuid-5',
                    'rank_data': {'tier': 'GOLD', 'rank': 'III', 'lp': 56, 'wins': 98, 'losses': 92},
                    'mastery_points': 150000,
                    'summoner_level': 142,
                    'is_target': False
                },
                # Red Team
                {
                    'teamId': 200,
                    'championId': 24,  # Jax
                    'spell1Id': 4,  # Flash
                    'spell2Id': 12,  # Teleport
                    'riotId': 'TopDiff#EUW',
                    'puuid': 'dummy-puuid-6',
                    'rank_data': {'tier': 'PLATINUM', 'rank': 'II', 'lp': 67, 'wins': 189, 'losses': 170},
                    'mastery_points': 380000,
                    'summoner_level': 267,
                    'is_target': False
                },
                {
                    'teamId': 200,
                    'championId': 121,  # Kha'Zix
                    'spell1Id': 4,  # Flash
                    'spell2Id': 11,  # Smite
                    'riotId': 'BugHunter#EUW',
                    'puuid': 'dummy-puuid-7',
                    'rank_data': {'tier': 'DIAMOND', 'rank': 'IV', 'lp': 12, 'wins': 234, 'losses': 210},
                    'mastery_points': 520000,
                    'summoner_level': 312,
                    'is_target': False
                },
                {
                    'teamId': 200,
                    'championId': 238,  # Zed
                    'spell1Id': 4,  # Flash
                    'spell2Id': 14,  # Ignite
                    'riotId': 'Zed',  # Streamer mode - name matches champion
                    'puuid': 'dummy-puuid-8',
                    'rank_data': {'tier': 'PLATINUM', 'rank': 'I', 'lp': 88, 'wins': 178, 'losses': 162},
                    'mastery_points': 410000,
                    'summoner_level': 245,
                    'is_target': False,
                    'perks': {
                        'perkIds': [8112, 8126, 8138, 8105, 8347, 8410],  # Has Cosmic Insight (8347)
                        'perkStyle': 8100,
                        'perkSubStyle': 8300
                    }
                },
                {
                    'teamId': 200,
                    'championId': 51,  # Caitlyn
                    'spell1Id': 4,  # Flash
                    'spell2Id': 7,  # Heal
                    'riotId': 'Sniper#EUW',
                    'puuid': 'dummy-puuid-9',
                    'rank_data': {'tier': 'GOLD', 'rank': 'I', 'lp': 71, 'wins': 156, 'losses': 148},
                    'mastery_points': 290000,
                    'summoner_level': 198,
                    'is_target': False,
                    'perks': {
                        'perkIds': [8005, 9111, 9104, 8014, 8347, 8451],  # Has Cosmic Insight (8347)
                        'perkStyle': 8000,
                        'perkSubStyle': 8300
                    }
                },
                {
                    'teamId': 200,
                    'championId': 89,  # Leona
                    'spell1Id': 4,  # Flash
                    'spell2Id': 14,  # Ignite
                    'riotId': 'SunGoddess#EUW',
                    'puuid': 'dummy-puuid-10',
                    'rank_data': {'tier': 'PLATINUM', 'rank': 'IV', 'lp': 23, 'wins': 134, 'losses': 125},
                    'mastery_points': 175000,
                    'summoner_level': 176,
                    'is_target': False
                }
            ]
        }
        
        # Display the dummy data
        LiveGameDisplay(self.live_game_content, dummy_data, self.rank_icons)

    def check_for_updates(self):
        """Check for updates in background"""
        def check():
            has_update, latest_version, download_url, release_notes, exe_url = self.update_checker.check_for_updates()
            
            if has_update:
                # Show update dialog on main thread
                self.root.after(0, lambda: self.show_update_dialog(latest_version, download_url, release_notes, exe_url))
        
        # Run check in background thread
        thread = threading.Thread(target=check, daemon=True)
        thread.start()
    
    def show_update_dialog(self, latest_version, download_url, release_notes, exe_url):
        """Show update notification dialog"""
        UpdateDialog(self.root, __version__, latest_version, download_url, release_notes, self.update_checker, exe_url)
