"""
Update notification dialog
"""
import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import sys

class UpdateDialog:
    def __init__(self, parent, current_version, latest_version, download_url, release_notes, update_checker, exe_url):
        self.parent_window = parent
        self.update_checker = update_checker
        self.download_url = download_url
        self.exe_url = exe_url
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Update Available")
        self.dialog.geometry("500x450")
        self.dialog.resizable(False, False)
        self.dialog.configure(bg="#2d2d2d")
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui(current_version, latest_version, release_notes)
    
    def setup_ui(self, current_version, latest_version, release_notes):
        """Setup the dialog UI"""
        # Main frame
        main_frame = tk.Frame(self.dialog, bg="#2d2d2d")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title = tk.Label(main_frame, text="🎉 New Version Available!", 
                        font=("Arial", 16, "bold"), bg="#2d2d2d", fg="#00ff88")
        title.pack(pady=(0, 10))
        
        # Version info
        version_frame = tk.Frame(main_frame, bg="#2d2d2d")
        version_frame.pack(pady=(0, 15))
        
        current_label = tk.Label(version_frame, text=f"Current Version: {current_version}", 
                                font=("Arial", 10), bg="#2d2d2d", fg="#aaaaaa")
        current_label.pack()
        
        latest_label = tk.Label(version_frame, text=f"Latest Version: {latest_version}", 
                               font=("Arial", 10, "bold"), bg="#2d2d2d", fg="#00bfff")
        latest_label.pack()
        
        # Release notes
        notes_label = tk.Label(main_frame, text="What's New:", 
                              font=("Arial", 11, "bold"), bg="#2d2d2d", fg="white")
        notes_label.pack(anchor="w", pady=(0, 5))
        
        notes_text = scrolledtext.ScrolledText(main_frame, 
                                               font=("Arial", 9),
                                               bg="#1e1e1e", fg="white",
                                               wrap=tk.WORD, height=8)
        notes_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        notes_text.insert("1.0", release_notes)
        notes_text.config(state=tk.DISABLED)
        
        # Progress bar (hidden initially)
        self.progress_frame = tk.Frame(main_frame, bg="#2d2d2d")
        
        self.progress_label = tk.Label(self.progress_frame, text="Downloading...", 
                                       font=("Arial", 9), bg="#2d2d2d", fg="#aaaaaa")
        self.progress_label.pack()
        
        self.progress_bar = tk.Canvas(self.progress_frame, width=460, height=20, 
                                     bg="#1e1e1e", highlightthickness=0)
        self.progress_bar.pack(pady=(5, 0))
        
        # Buttons
        self.btn_frame = tk.Frame(main_frame, bg="#2d2d2d")
        self.btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.install_btn = tk.Button(self.btn_frame, text="Install Update", 
                                command=self.install_update,
                                bg="#28a745", fg="white", font=("Arial", 11, "bold"),
                                padx=20, pady=10, relief=tk.FLAT, cursor="hand2")
        self.install_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        manual_btn = tk.Button(self.btn_frame, text="Download Manually", 
                              command=self.download_manually,
                              bg="#0078d4", fg="white", font=("Arial", 11),
                              padx=20, pady=10, relief=tk.FLAT, cursor="hand2")
        manual_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.later_btn = tk.Button(self.btn_frame, text="Later", 
                             command=self.dialog.destroy,
                             bg="#4a4a4a", fg="white", font=("Arial", 11),
                             padx=20, pady=10, relief=tk.FLAT, cursor="hand2")
        self.later_btn.pack(side=tk.LEFT)
    
    def install_update(self):
        """Automatically download and install update"""
        if not self.exe_url:
            messagebox.showerror("Error", "Could not find download URL. Please download manually.")
            return
        
        # Show progress bar
        self.progress_frame.pack(fill=tk.X, pady=(0, 10))
        self.install_btn.config(state=tk.DISABLED)
        self.later_btn.config(state=tk.DISABLED)
        
        # Download in background thread
        def download():
            success = self.update_checker.download_and_install_update(
                self.exe_url, 
                progress_callback=self.update_progress
            )
            
            if success:
                # Close the app to allow update
                self.dialog.after(0, self.close_and_update)
            else:
                self.dialog.after(0, lambda: messagebox.showerror(
                    "Update Failed", 
                    "Failed to download update. Please try downloading manually."
                ))
                self.dialog.after(0, self.reset_buttons)
        
        thread = threading.Thread(target=download, daemon=True)
        thread.start()
    
    def update_progress(self, downloaded, total):
        """Update progress bar"""
        if total > 0:
            progress = downloaded / total
            self.progress_bar.delete("all")
            bar_width = int(460 * progress)
            self.progress_bar.create_rectangle(0, 0, bar_width, 20, fill="#28a745", outline="")
            
            percent = int(progress * 100)
            self.progress_label.config(text=f"Downloading... {percent}%")
    
    def close_and_update(self):
        """Close the application to allow update"""
        messagebox.showinfo("Update Ready", 
                           "Update downloaded! The application will now restart to complete the update.")
        self.dialog.destroy()
        # Exit the entire application
        sys.exit(0)
    
    def reset_buttons(self):
        """Reset buttons after failed download"""
        self.progress_frame.pack_forget()
        self.install_btn.config(state=tk.NORMAL)
        self.later_btn.config(state=tk.NORMAL)
    
    def download_manually(self):
        """Open download page in browser"""
        self.update_checker.open_download_page(self.download_url)
        self.dialog.destroy()
