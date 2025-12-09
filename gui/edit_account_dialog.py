import tkinter as tk
from tkinter import ttk, messagebox

class EditAccountDialog:
    def __init__(self, parent, account_manager, account):
        self.account_manager = account_manager
        self.account = account
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Edit Account")
        self.dialog.geometry("450x650")
        self.dialog.resizable(True, True)
        self.dialog.configure(bg="#2d2d2d")
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the dialog UI"""
        # Main frame
        main_frame = tk.Frame(self.dialog, bg="#2d2d2d")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title = tk.Label(main_frame, text="Edit Account", 
                        font=("Arial", 14, "bold"), bg="#2d2d2d", fg="white")
        title.pack(pady=(0, 20))
        
        # Username
        self.create_field(main_frame, "Username (Session ID):", "username", 
                         self.account.get("username", ""))
        
        # Display Name
        self.create_field(main_frame, "Display Name:", "display_name", 
                         self.account.get("display_name", ""))
        
        # Riot ID
        self.create_field(main_frame, "Riot ID for rank (e.g. Name#TAG):", "riot_id", 
                         self.account.get("riot_id", ""))
        
        # Password (optional)
        self.create_field(main_frame, "Password (optional, for quick copy):", "password", 
                         self.account.get("password", ""), show="*")
        
        # Buttons
        btn_frame = tk.Frame(main_frame, bg="#2d2d2d")
        btn_frame.pack(pady=(30, 10), fill=tk.X)
        
        save_btn = tk.Button(btn_frame, text="Save Changes", 
                            command=self.save_account,
                            bg="#0078d4", fg="white", font=("Arial", 11, "bold"),
                            padx=25, pady=10, relief=tk.FLAT, cursor="hand2")
        save_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        cancel_btn = tk.Button(btn_frame, text="Cancel", 
                              command=self.dialog.destroy,
                              bg="#4a4a4a", fg="white", font=("Arial", 11),
                              padx=25, pady=10, relief=tk.FLAT, cursor="hand2")
        cancel_btn.pack(side=tk.LEFT)
        
        # Delete button (on the right)
        delete_btn = tk.Button(btn_frame, text="Delete Account", 
                              command=self.delete_account,
                              bg="#d13438", fg="white", font=("Arial", 11),
                              padx=25, pady=10, relief=tk.FLAT, cursor="hand2")
        delete_btn.pack(side=tk.RIGHT)
    
    def create_field(self, parent, label_text, field_name, default_value="", show=None):
        """Create a labeled input field"""
        frame = tk.Frame(parent, bg="#2d2d2d")
        frame.pack(fill=tk.X, pady=(0, 8))
        
        label = tk.Label(frame, text=label_text, 
                        font=("Arial", 9), bg="#2d2d2d", fg="#aaaaaa")
        label.pack(anchor="w", pady=(0, 3))
        
        entry = tk.Entry(frame, font=("Arial", 10), bg="#1e1e1e", fg="white",
                        insertbackground="white", relief=tk.FLAT, show=show)
        entry.insert(0, default_value)
        entry.pack(fill=tk.X, ipady=5)
        
        setattr(self, f"{field_name}_entry", entry)
    
    def save_account(self):
        """Save the account changes"""
        username = self.username_entry.get().strip()
        
        if not username:
            messagebox.showerror("Error", "Username is required!")
            return
        
        display_name = self.display_name_entry.get().strip()
        riot_id = self.riot_id_entry.get().strip()
        password = self.password_entry.get().strip()
        
        self.account_manager.update_account(
            self.account["id"],
            username=username,
            display_name=display_name or username,
            riot_id=riot_id,
            password=password
        )
        
        # Account updated silently, no popup
        self.dialog.destroy()
    
    def delete_account(self):
        """Delete the account"""
        if messagebox.askyesno("Confirm Delete", 
                              f"Are you sure you want to delete '{self.account['display_name']}'?"):
            self.account_manager.delete_account(self.account["id"])
            self.dialog.destroy()
