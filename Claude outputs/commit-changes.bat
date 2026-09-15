@echo off
setlocal enabledelayedexpansion

:: Commit this build and push it to GitHub.
:: Double-click, or run:  commit-changes.bat "your own message"

cd /d "%~dp0"

echo =======================================================
echo   Fantrade - commit and push
echo   %CD%
echo =======================================================
echo.

git rev-parse --is-inside-work-tree >nul 2>&1
if errorlevel 1 (
    echo [ERROR] This folder is not a git repository.
    echo.
    pause
    exit /b 1
)

echo Current branch:
git rev-parse --abbrev-ref HEAD
echo.

echo Changes in the working tree:
git status --short
echo.

for /f %%i in ('git status --porcelain ^| find /c /v ""') do set COUNT=%%i

if "!COUNT!"=="0" (
    echo [INFO] Nothing to commit. Pushing any local commits that are ahead.
    goto :push
)

set "MSG=%~1"
if "!MSG!"=="" set "MSG=Rename Fantrade Points to Fans Point; rebuild the trade terminal"

echo Staging !COUNT! change(s)...
git add -A
if errorlevel 1 goto :failed

echo Committing: "!MSG!"
git commit -m "!MSG!"
if errorlevel 1 goto :failed

:push
echo.
echo Pushing to origin...
for /f %%b in ('git rev-parse --abbrev-ref HEAD') do set BRANCH=%%b
git push origin !BRANCH!
if errorlevel 1 goto :failed

echo.
echo =======================================================
echo   Pushed !BRANCH! to GitHub.
echo   https://github.com/vicethetechguy/Fantrade
echo =======================================================
echo.
pause
exit /b 0

:failed
echo.
echo [ERROR] That step failed - nothing further was run.
echo Check the message above, then try again.
echo.
pause
exit /b 1
