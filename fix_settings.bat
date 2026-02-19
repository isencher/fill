@echo off
echo ========================================
echo Claude Settings Fix for Windows
echo ========================================
echo.

REM Check if we're in the fill project directory
if not exist "src\main.py" (
    echo ERROR: Please run this script from the fill project root directory
    echo Example: cd D:\.dev\fill
    pause
    exit /b 1
)

echo Step 1: Backing up current settings...
copy ".claude\settings.json" ".claude\settings.json.backup" >nul 2>&1
echo Backup created: .claude\settings.json.backup
echo.

echo Step 2: Fetching latest from remote...
git fetch origin
echo.

echo Step 3: Getting correct settings from remote...
git show origin/master:.claude/settings.json > ".claude\settings.json.tmp"
if %errorlevel% neq 0 (
    echo ERROR: Failed to get settings from remote
    pause
    exit /b 1
)
echo.

echo Step 4: Updating settings.json...
move /Y ".claude\settings.json.tmp" ".claude\settings.json" >nul
echo.

echo Step 5: Verifying the fix...
findstr /C:"\"PreToolUse\": [" .claude\settings.json >nul
if %errorlevel% equ 0 (
    echo SUCCESS: Settings file has been FIXED!
    echo.
    echo The file now has the correct array format.
    echo.
    echo NEXT STEPS:
    echo 1. Close ALL Claude Code windows
    echo 2. Restart Claude Code
    echo 3. The settings error should be gone
    echo.
) else (
    echo WARNING: Verification failed
    echo Please check the file manually: type .claude\settings.json
    echo.
)

echo Press any key to exit...
pause >nul
