"""
Build script for creating standalone executable
Run: python build_exe.py
"""
import PyInstaller.__main__
import os
import shutil

# Clean previous builds
if os.path.exists('build'):
    shutil.rmtree('build')
if os.path.exists('dist'):
    shutil.rmtree('dist')

# PyInstaller arguments - using --onedir to avoid temp directory warnings
PyInstaller.__main__.run([
    'main.py',
    '--name=RiotAccountManager',
    '--onedir',  # Directory mode - no temp folder warnings
    '--windowed',  # No console window
    '--icon=assets/rose.ico',
    '--add-data=assets;assets',  # Include assets folder
    '--hidden-import=PIL._tkinter_finder',
    '--hidden-import=pyperclip',
    '--collect-all=tkinter',
    '--noconfirm',
])

print("\n" + "="*50)
print("Build complete!")
print("Executable location: dist/RiotAccountManager/RiotAccountManager.exe")
print("\nTo distribute: Zip the entire 'dist/RiotAccountManager' folder")
print("="*50)
