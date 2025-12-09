import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import sys
import warnings
from pathlib import Path
from account_manager import AccountManager
from gui.main_window import MainWindow

# Suppress PyInstaller warnings
warnings.filterwarnings("ignore")

def main():
    root = tk.Tk()
    root.title("Riot Account Manager")
    root.geometry("1000x630")
    root.minsize(900, 580)
    
    # Initialize account manager
    account_manager = AccountManager()
    
    # Create main window
    app = MainWindow(root, account_manager)
    
    # Suppress cleanup warnings on exit
    def on_closing():
        try:
            root.destroy()
        except:
            pass
        sys.exit(0)
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
