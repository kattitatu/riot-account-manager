# Release Guide

This guide explains how to create releases for the auto-update system.

## Prerequisites

1. Build the executable using PyInstaller:
```bash
python build_exe.py
```

2. The executable will be in `dist/RiotAccountManager.exe`

## Creating a Release on GitHub

### Step 1: Update Version

1. Edit `version.py` and increment the version number:
```python
__version__ = "1.0.1"  # Increment this
```

2. Commit the version change:
```bash
git add version.py
git commit -m "Bump version to 1.0.1"
git push
```

### Step 2: Create a Git Tag

```bash
git tag -a v1.0.1 -m "Release version 1.0.1"
git push origin v1.0.1
```

### Step 3: Create GitHub Release

1. Go to your GitHub repository
2. Click on "Releases" in the right sidebar
3. Click "Create a new release"
4. Select the tag you just created (v1.0.1)
5. Set the release title (e.g., "Version 1.0.1")
6. Add release notes describing what's new:

```markdown
## What's New

### Features
- Added summoner spell tracker
- Improved live game display

### Bug Fixes
- Fixed account switching issue
- Improved error handling

### Changes
- Updated UI layout
- Performance improvements
```

7. Attach the executable:
   - Click "Attach binaries"
   - Upload `dist/RiotAccountManager.exe`

8. Click "Publish release"

## Auto-Update Configuration

Make sure to update the GitHub repository name in `gui/main_window.py`:

```python
self.update_checker = UpdateChecker("yourusername/riot-account-manager")
```

Replace `yourusername/riot-account-manager` with your actual GitHub repository.

## Version Numbering

Follow semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backwards compatible)
- **PATCH**: Bug fixes (backwards compatible)

Examples:
- `1.0.0` → `1.0.1` (bug fix)
- `1.0.1` → `1.1.0` (new feature)
- `1.1.0` → `2.0.0` (breaking change)

## Testing Auto-Update

1. Set version to something lower (e.g., `0.9.0`)
2. Build and run the application
3. Create a release with version `1.0.0`
4. The application should detect the update on startup
5. Click "Download Update" to test the download link

## Troubleshooting

### Update not detected
- Check that the tag starts with 'v' (e.g., v1.0.1)
- Verify the GitHub repository name is correct
- Check internet connection

### Download link not working
- Make sure you attached the .exe file to the release
- Verify the release is published (not draft)
