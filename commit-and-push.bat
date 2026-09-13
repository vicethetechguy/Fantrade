@echo off
setlocal enabledelayedexpansion

:: Navigate to repository directory
cd /d "%~dp0"

echo =======================================================
echo          Fantrade - Easy Commit and Push to GitHub
echo =======================================================
echo.

:: Check git status
git status --short > temp_status.txt
set /p STATUS=<temp_status.txt
if exist temp_status.txt del temp_status.txt

if "!STATUS!"=="" (
    echo [INFO] No new changes detected in local working tree.
    echo Pushing any unpushed local commits to GitHub...
) else (
    echo [CHANGES DETECTED]:
    git status --short
    echo.
    
    :: Get commit message from argument or prompt user
    set "COMMIT_MSG=%~1"
    if "!COMMIT_MSG!"=="" (
        set /p COMMIT_MSG="Enter commit message (or press ENTER for default): "
    )
    
    if "!COMMIT_MSG!"=="" (
        set "COMMIT_MSG=Update Fantrade project files"
    )
    
    echo.
    echo Staging files...
    git add -A
    
    echo Committing with message: "!COMMIT_MSG!"
    git commit -m "!COMMIT_MSG!"
)

echo.
echo Pushing to GitHub (origin/main)...
git push origin main

if %ERRORLEVEL% equ 0 (
    echo.
    echo =======================================================
    echo  SUCCESS! Pushed successfully to GitHub!
    echo  View repository: https://github.com/vicethetechguy/Fantrade
    echo =======================================================
) else (
    echo.
    echo [ERROR] Push failed. Check your network or git configuration.
)

echo.
pause
