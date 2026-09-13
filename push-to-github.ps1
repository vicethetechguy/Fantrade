param(
    [string]$Message = "Update Fantrade project files",
    [string]$Branch = "main"
)

$ErrorActionPreference = "Stop"

$repo = $PSScriptRoot
Set-Location -LiteralPath $repo

Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "         Fantrade - PowerShell Commit & Push" -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host ""

$status = git status --short
if ([string]::IsNullOrWhiteSpace($status)) {
    Write-Host "[INFO] No unstaged/uncommitted changes detected." -ForegroundColor Yellow
    Write-Host "Pushing any unpushed local commits to GitHub..." -ForegroundColor Yellow
} else {
    Write-Host "[CHANGES DETECTED]:" -ForegroundColor Green
    git status --short
    Write-Host ""
    
    Write-Host "Staging all files..." -ForegroundColor Yellow
    git add -A
    
    Write-Host "Committing with message: '$Message'..." -ForegroundColor Yellow
    git commit -m $Message
}

Write-Host ""
Write-Host "Pushing to GitHub (origin/$Branch)..." -ForegroundColor Cyan
git push origin $Branch

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=======================================================" -ForegroundColor Green
    Write-Host "  SUCCESS! Pushed successfully to GitHub!" -ForegroundColor Green
    Write-Host "  View repo: https://github.com/vicethetechguy/Fantrade" -ForegroundColor Green
    Write-Host "=======================================================" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Push failed." -ForegroundColor Red
}
