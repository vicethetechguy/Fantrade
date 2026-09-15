@echo off
:: Opens a Command Prompt already sitting in the Fantrade folder.
:: Double-click this file, then run: commit-and-push.bat
cd /d "%~dp0"

echo =======================================================
echo   Fantrade
echo   %CD%
echo =======================================================
echo.
echo   commit-and-push.bat            commit and push to GitHub
echo   commit-and-push.bat "message"  same, with your own message
echo   git status                     see what changed
echo.

cmd /k
