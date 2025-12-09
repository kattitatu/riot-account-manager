@echo off
echo ========================================
echo Riot Account Manager - Build Script
echo ========================================
echo.

echo Installing build dependencies...
python -m pip install -r build_requirements.txt
echo.

echo Building executable...
python build_exe.py
echo.

echo ========================================
echo Build Complete!
echo.
echo Your executable is located at:
echo dist\RiotAccountManager.exe
echo ========================================
echo.
pause
