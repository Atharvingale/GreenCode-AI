# GreenCode AI - Project Cleanup Script
# This script removes unnecessary files and folders to reduce project size

Write-Host "🧹 Starting GreenCode AI Project Cleanup..." -ForegroundColor Green
Write-Host ""

$projectPath = "C:\Users\ingal\Desktop\Projects\GREENCODE AI"
Set-Location $projectPath

# Function to safely remove directory/file
function Remove-SafelyWithConfirmation {
    param(
        [string]$Path,
        [string]$Description
    )
    
    if (Test-Path $Path) {
        $size = if (Test-Path $Path -PathType Container) {
            (Get-ChildItem $Path -Recurse -Force | Measure-Object -Property Length -Sum).Sum
        } else {
            (Get-Item $Path).Length
        }
        
        $sizeGB = [math]::Round($size / 1GB, 2)
        $sizeMB = [math]::Round($size / 1MB, 2)
        $displaySize = if ($sizeGB -gt 0.1) { "$sizeGB GB" } else { "$sizeMB MB" }
        
        Write-Host "🔍 Found: $Description - Size: $displaySize" -ForegroundColor Yellow
        $confirmation = Read-Host "   Delete? (y/N)"
        
        if ($confirmation -eq 'y' -or $confirmation -eq 'Y') {
            try {
                Remove-Item $Path -Recurse -Force
                Write-Host "   ✅ Deleted successfully" -ForegroundColor Green
                return $size
            }
            catch {
                Write-Host "   ❌ Failed to delete: $($_.Exception.Message)" -ForegroundColor Red
                return 0
            }
        } else {
            Write-Host "   ⏭️ Skipped" -ForegroundColor Gray
            return 0
        }
    } else {
        Write-Host "   ℹ️ Not found: $Path" -ForegroundColor Gray
        return 0
    }
}

# Track total space saved
$totalSaved = 0

Write-Host "1️⃣ Cleaning up session data folders..." -ForegroundColor Cyan
Write-Host ""

# Clean up old session folders in data/
$sessionFolders = Get-ChildItem "data" -Directory -Name "session_*" -ErrorAction SilentlyContinue | Sort-Object
if ($sessionFolders.Count -gt 1) {
    Write-Host "   Found $($sessionFolders.Count) session folders. Keeping the most recent one..." -ForegroundColor Yellow
    
    # Keep the most recent session, delete the rest
    for ($i = 0; $i -lt ($sessionFolders.Count - 1); $i++) {
        $folderPath = "data/$($sessionFolders[$i])"
        $totalSaved += Remove-SafelyWithConfirmation $folderPath "Old session data: $($sessionFolders[$i])"
    }
} else {
    Write-Host "   ✅ Session data already clean" -ForegroundColor Green
}

Write-Host ""
Write-Host "2️⃣ Cleaning up temporary uploads..." -ForegroundColor Cyan
Write-Host ""

# Clean up temp_uploads completely (it will be recreated when needed)
$totalSaved += Remove-SafelyWithConfirmation "temp_uploads" "Temporary upload files"

Write-Host ""
Write-Host "3️⃣ Cleaning up legacy/backup UI files..." -ForegroundColor Cyan
Write-Host ""

# Clean up backup UI files
$totalSaved += Remove-SafelyWithConfirmation "ui/app_backup.py" "UI backup file"
$totalSaved += Remove-SafelyWithConfirmation "ui/app_redesigned.py" "UI redesigned file"
$totalSaved += Remove-SafelyWithConfirmation "ui/app.txt" "UI text file"

Write-Host ""
Write-Host "4️⃣ Cleaning up Python cache files..." -ForegroundColor Cyan
Write-Host ""

# Clean up Python cache
Get-ChildItem -Path . -Name "__pycache__" -Recurse -Directory -Force | ForEach-Object {
    $fullPath = $_.FullName
    $totalSaved += Remove-SafelyWithConfirmation $fullPath "Python cache: $($_.Name)"
}

Write-Host ""
Write-Host "5️⃣ Checking frontend folder..." -ForegroundColor Cyan
Write-Host ""

# Check if frontend is being used
$frontendSize = if (Test-Path "frontend") {
    (Get-ChildItem "frontend" -Recurse -Force | Measure-Object -Property Length -Sum).Sum
} else { 0 }

if ($frontendSize -gt 0) {
    $frontendSizeMB = [math]::Round($frontendSize / 1MB, 2)
    Write-Host "   Found frontend folder ($frontendSizeMB MB). This appears to be an incomplete Next.js project." -ForegroundColor Yellow
    Write-Host "   If you're not using the frontend, consider removing it." -ForegroundColor Yellow
    $totalSaved += Remove-SafelyWithConfirmation "frontend" "Next.js frontend project"
}

Write-Host ""
Write-Host "6️⃣ Cleaning up other unnecessary files..." -ForegroundColor Cyan
Write-Host ""

# Clean up other files
$totalSaved += Remove-SafelyWithConfirmation "config" "Config folder (if not needed)"
$totalSaved += Remove-SafelyWithConfirmation "test_html.py" "Test HTML file"

# Clean up any .pyc files
Get-ChildItem -Path . -Name "*.pyc" -Recurse -Force | ForEach-Object {
    $totalSaved += Remove-SafelyWithConfirmation $_.FullName "Python compiled file: $($_.Name)"
}

Write-Host ""
Write-Host "🎯 Cleanup Summary:" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green

$savedGB = [math]::Round($totalSaved / 1GB, 2)
$savedMB = [math]::Round($totalSaved / 1MB, 2)
$displaySaved = if ($savedGB -gt 0.1) { "$savedGB GB" } else { "$savedMB MB" }

Write-Host "✅ Total space saved: $displaySaved" -ForegroundColor Green
Write-Host ""
Write-Host "📂 Current project structure:" -ForegroundColor Cyan
tree /F /A . | Select-Object -First 30
Write-Host ""
Write-Host "🏁 Cleanup completed! Your project is now cleaner and more organized." -ForegroundColor Green
Write-Host "   Remember to run 'git add .' to stage the .gitignore changes." -ForegroundColor Yellow

Read-Host "`nPress Enter to exit"