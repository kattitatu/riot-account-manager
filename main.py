import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from pathlib import Path
from account_manager import AccountManager
from gui.main_window import MainWindow

def main():
    root = tk.Tk()
    root.title("Riot Account Manager")
    root.geometry("1000x630")
    root.minsize(900, 580)
    
    # Initialize account manager
    account_manager = AccountManager()
    
    # Create main window
    app = MainWindow(root, account_manager)
    
    root.mainloop()

if __name__ == "__main__":
    main()
