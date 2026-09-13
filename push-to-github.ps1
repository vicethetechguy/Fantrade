param(
  [string]$Message = "Rebrand to #1800AD palette, cinematic gradients, asset hooks, mobile fixes",
  [string]$Branch = "main",
  [switch]$NoCommit
)

$ErrorActionPreference = "Stop"

$repo = "C:\Users\user\Downloads\Fantrade New"
Set-Location -LiteralPath $repo

Write-Host "Preparing Fantrade changes..."
git add -A
git status --short

if (-not $NoCommit) {
  git diff --cached --quiet
  $diffExitCode = $LASTEXITCODE

  if ($diffExitCode -eq 0) {
    Write-Host "No staged changes to commit. Continuing to push $Branch."
  } elseif ($diffExitCode -eq 1) {
    git commit -m $Message
    if ($LASTEXITCODE -ne 0) {
      throw "Commit failed."
    }
  } else {
    throw "Could not inspect staged changes."
  }
}

$secureToken = Read-Host "Paste your GitHub fine-grained token" -AsSecureString
$tokenPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureToken)

try {
  $token = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($tokenPointer)
} finally {
  [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($tokenPointer)
}

if ([string]::IsNullOrWhiteSpace($token)) {
  throw "No token entered."
}

$askPass = Join-Path $env:TEMP ("fantrade-git-askpass-" + [guid]::NewGuid() + ".cmd")

try {
  @"
@echo off
setlocal
set "prompt=%~1"
echo %prompt% | find /I "Username" >nul
if %errorlevel%==0 (
  echo x-access-token
  exit /b 0
)
echo %prompt% | find /I "Password" >nul
if %errorlevel%==0 (
  powershell -NoProfile -ExecutionPolicy Bypass -Command "[Console]::Out.Write(`$env:GITHUB_FINE_GRAINED_TOKEN)"
  exit /b 0
)
exit /b 1
"@ | Set-Content -LiteralPath $askPass -Encoding ASCII -NoNewline

  $env:GIT_ASKPASS = $askPass
  $env:GIT_TERMINAL_PROMPT = "0"
  $env:GCM_INTERACTIVE = "Never"
  $env:GITHUB_FINE_GRAINED_TOKEN = $token

  Write-Host "Pushing to origin/$Branch with token authentication..."
  git -c credential.helper= push origin $Branch

  if ($LASTEXITCODE -ne 0) {
    throw "Push failed. Check that the fine-grained token has access to vicethetechguy/Fantrade and Contents read/write permission."
  }

  Write-Host "Push complete."
} finally {
  Remove-Item Env:\GIT_ASKPASS -ErrorAction SilentlyContinue
  Remove-Item Env:\GIT_TERMINAL_PROMPT -ErrorAction SilentlyContinue
  Remove-Item Env:\GCM_INTERACTIVE -ErrorAction SilentlyContinue
  Remove-Item Env:\GITHUB_FINE_GRAINED_TOKEN -ErrorAction SilentlyContinue
  if (Test-Path -LiteralPath $askPass) {
    Remove-Item -LiteralPath $askPass -Force
  }
}
