"""Test update checker"""
from update_checker import UpdateChecker

# Test the update checker
checker = UpdateChecker("kattitatu/riot-account-manager")

print("Testing update checker...")
print(f"Current version: {checker.current_version}")
print(f"API URL: {checker.api_url}")
print()

has_update, latest_version, download_url, release_notes, exe_url = checker.check_for_updates()

print(f"Has update: {has_update}")
print(f"Latest version: {latest_version}")
print(f"Download URL: {download_url}")
print(f"EXE URL: {exe_url}")
print()

if has_update:
    print("✓ Update detected!")
else:
    print("✗ No update detected")
    print(f"Current: {checker.current_version}, Latest: {latest_version}")
