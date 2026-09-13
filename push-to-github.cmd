@echo off
set "REPO=C:\Users\user\Downloads\Fantrade New"
powershell -NoProfile -ExecutionPolicy Bypass -File "%REPO%\push-to-github.ps1" %*
pause
