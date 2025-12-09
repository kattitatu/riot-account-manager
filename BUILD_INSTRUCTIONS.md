# Building Riot Account Manager as .exe

## Prerequisites
- Python 3.7 or higher installed
- All project files in the same directory

## Step 1: Install Build Dependencies

Open Command Prompt or PowerShell in the project directory and run:

```bash
pip install -r build_requirements.txt
```

This will install:
- PyInstaller (for creating the .exe)
- All application dependencies (requests, beautifulsoup4, Pillow)

## Step 2: Build the Executable

Run the build script:

```bash
python build_exe.py
```

This will:
- Clean previous builds
- Create a standalone .exe file
- Include all dependencies
- Bundle the assets folder (rank icons)

## Step 3: Find Your Executable

After building, you'll find:
- **Executable**: `dist/RiotAccountManager.exe`
- This is a standalone file that can run on any Windows PC without Python installed

## Step 4: Distribution

To share with friends:

1. **Option A - Just the .exe (Recommended)**:
   - Copy `dist/RiotAccountManager.exe` to a new folder
   - If you have rank icons, create `assets/ranks/` folder next to the .exe and add the PNG files
   - Share the folder

2. **Option B - With rank icons included**:
   - Copy `dist/RiotAccountManager.exe`
   - Copy the `assets` folder (with rank icons) to the same location
   - Share both together

## Notes

- The .exe is about 15-25 MB (includes Python runtime and all libraries)
- First launch might be slower (Windows security scan)
- No Python installation needed on target computers
- Account data (`accounts.json`) and session backups are created automatically on first run

## Troubleshooting

**If build fails:**
1. Make sure all Python files are in the project directory
2. Check that all imports work: `python main.py`
3. Try updating PyInstaller: `pip install --upgrade pyinstaller`

**If .exe doesn't run:**
1. Windows Defender might block it (add exception)
2. Run as administrator if needed
3. Check antivirus software

**To reduce .exe size:**
- Remove unused dependencies
- Use `--onedir` instead of `--onefile` in build_exe.py (creates folder with multiple files but smaller main exe)

## Advanced: Adding an Icon

1. Get a .ico file (256x256 recommended)
2. Save it as `icon.ico` in the project folder
3. Edit `build_exe.py` and change `'--icon=NONE'` to `'--icon=icon.ico'`
4. Rebuild
