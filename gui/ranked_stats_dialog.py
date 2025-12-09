import tkinter as tk

class RankedStatsDialog:
    def __init__(self, parent, account):
        self.account = account
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Ranked Stats - {account.get('display_name', 'Unknown')}")
        self.dialog.geometry("350x300")
        self.dialog.resizable(False, False)
        self.dialog.configure(bg="#2d2d2d")
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the stats dialog UI"""
        main_frame = tk.Frame(self.dialog, bg="#2d2d2d")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title = tk.Label(main_frame, text="Ranked Solo/Duo Stats", 
                        font=("Arial", 14, "bold"), bg="#2d2d2d", fg="white")
        title.pack(pady=(0, 20))
        
        ranked_stats = self.account.get('ranked_stats')
        
        if not ranked_stats:
            no_data_label = tk.Label(main_frame, text="No ranked data available", 
                                    font=("Arial", 10), bg="#2d2d2d", fg="#888888")
            no_data_label.pack(pady=20)
        else:
            # Rank
            tier = ranked_stats.get('tier', 'Unranked')
            division = ranked_stats.get('division', '')
            rank_text = f"{tier} {division}" if division else tier
            
            rank_label = tk.Label(main_frame, text=rank_text, 
                                 font=("Arial", 24, "bold"), bg="#2d2d2d", fg="#ffd700")
            rank_label.pack(pady=(0, 20))
            
            # LP
            lp = ranked_stats.get('lp', 0)
            lp_label = tk.Label(main_frame, text=f"{lp} LP", 
                               font=("Arial", 12), bg="#2d2d2d", fg="#aaaaaa")
            lp_label.pack(pady=(0, 20))
            
            # Wins/Losses
            wins = ranked_stats.get('wins', 0)
            losses = ranked_stats.get('losses', 0)
            total = wins + losses
            winrate = (wins / total * 100) if total > 0 else 0
            
            stats_frame = tk.Frame(main_frame, bg="#2d2d2d")
            stats_frame.pack(pady=(0, 10))
            
            wins_label = tk.Label(stats_frame, text=f"Wins: {wins}", 
                                 font=("Arial", 11), bg="#2d2d2d", fg="#28a745")
            wins_label.grid(row=0, column=0, padx=10)
            
            losses_label = tk.Label(stats_frame, text=f"Losses: {losses}", 
                                   font=("Arial", 11), bg="#2d2d2d", fg="#d13438")
            losses_label.grid(row=0, column=1, padx=10)
            
            # Winrate
            winrate_label = tk.Label(main_frame, text=f"Win Rate: {winrate:.1f}%", 
                                    font=("Arial", 12, "bold"), bg="#2d2d2d", fg="white")
            winrate_label.pack(pady=(10, 0))
        
        # Close button
        close_btn = tk.Button(main_frame, text="Close", 
                             command=self.dialog.destroy,
                             bg="#4a4a4a", fg="white", font=("Arial", 10),
                             padx=20, pady=8, relief=tk.FLAT, cursor="hand2")
        close_btn.pack(pady=(20, 0))
