# Claude Settings Fix Script for Windows
# Run this script in PowerShell to fix Claude Code settings error

Write-Host "=== Claude Settings Fix for Windows ===" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the fill project directory
if (!(Test-Path "src\main.py")) {
    Write-Host "ERROR: Please run this script from the fill project root directory" -ForegroundColor Red
    Write-Host "Example: cd D:\.dev\fill" -ForegroundColor Yellow
    exit 1
}

# Check if settings.json exists
$settingsPath = ".claude\settings.json"
if (!(Test-Path $settingsPath)) {
    Write-Host "ERROR: $settingsPath not found" -ForegroundColor Red
    exit 1
}

Write-Host "Step 1: Checking current settings format..." -ForegroundColor Yellow
$currentSettings = Get-Content $settingsPath -Raw

# Check if settings has old format (object instead of array)
if ($currentSettings -match '`"PreToolUse"`\s*:\s*\{') {
    Write-Host "  Detected OLD format (will be fixed)" -ForegroundColor Red
} elseif ($currentSettings -match '`"PreToolUse"`\s*:\s*\[') {
    Write-Host "  Current format is CORRECT (array-based)" -ForegroundColor Green
} else {
    Write-Host "  Unable to detect format" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Step 2: Pulling latest changes from remote..." -ForegroundColor Yellow
git fetch origin
git pull origin master

Write-Host ""
Write-Host "Step 3: Verifying settings.json format..." -ForegroundColor Yellow

# Read the file again after pull
$newSettings = Get-Content $settingsPath -Raw

if ($newSettings -match '`"PreToolUse"`\s*:\s*\[') {
    Write-Host "  SUCCESS: Settings format is CORRECT" -ForegroundColor Green

    # Count the hooks
    $preToolUse = ($newSettings | Select-String '"PreToolUse"' -AllMatches).Matches.Count
    $postToolUse = ($newSettings | Select-String '"PostToolUse"' -AllMatches).Matches.Count
    $userPromptSubmit = ($newSettings | Select-String '"UserPromptSubmit"' -AllMatches).Matches.Count

    Write-Host "  PreToolUse hooks: $preToolUse" -ForegroundColor Cyan
    Write-Host "  PostToolUse hooks: $postToolUse" -ForegroundColor Cyan
    Write-Host "  UserPromptSubmit hooks: $userPromptSubmit" -ForegroundColor Cyan
} else {
    Write-Host "  WARNING: Settings format may still be incorrect" -ForegroundColor Yellow
    Write-Host "  Attempting direct fix..." -ForegroundColor Yellow

    # Backup current file
    $backupPath = $settingsPath + ".backup"
    Copy-Item $settingsPath $backupPath
    Write-Host "  Backup created: $backupPath" -ForegroundColor Cyan

    # Write correct settings
    $correctSettings = @'
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": {
          "tools": ["BashTool", "TaskTool", "ReadTool", "WriteTool", "EditTool"]
        },
        "hooks": []
      }
    ],
    "PostToolUse": [
      {
        "matcher": {
          "tools": ["BashTool", "TaskTool", "ReadTool", "WriteTool", "EditTool"]
        },
        "hooks": []
      }
    ],
    "UserPromptSubmit": [
      {
        "matcher": {},
        "hooks": []
      }
    ]
  },
  "mcpServers": {}
}
'@

    Set-Content -Path $settingsPath -Value $correctSettings -Encoding UTF8
    Write-Host "  Settings file has been FIXED" -ForegroundColor Green
}

Write-Host ""
Write-Host "Step 4: Verification..." -ForegroundColor Yellow

# Verify the fix
$finalSettings = Get-Content $settingsPath -Raw
if ($finalSettings -match '`"PreToolUse"`\s*:\s*\[' -and
    $finalSettings -match '`"matcher"`' -and
    $finalSettings -match '`"tools"`') {
    Write-Host "  Settings.json is correctly formatted!" -ForegroundColor Green
} else {
    Write-Host "  ERROR: Settings format could not be verified" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=== Fix Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "NEXT STEPS:" -ForegroundColor Cyan
Write-Host "1. Close ALL Claude Code windows" -ForegroundColor Yellow
Write-Host "2. Restart Claude Code" -ForegroundColor Yellow
Write-Host "3. Open the fill project (D:\.dev\fill)" -ForegroundColor Yellow
Write-Host ""
Write-Host "The settings error should now be resolved!" -ForegroundColor Green
Write-Host ""
