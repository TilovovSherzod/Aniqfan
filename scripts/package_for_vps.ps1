# PowerShell packaging script for Windows
# Usage: .\scripts\package_for_vps.ps1 -OutPath ..\sayt-deploy.zip
param(
  [string]$OutPath = "..\sayt-deploy.zip"
)

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location "$root\.."

Write-Host "Creating zip: $OutPath"

# Build list of files to exclude
$excludes = @(
  ".venv",
  ".git",
  "__pycache__",
  "*.pyc",
  "*.sqlite3",
  "media",
  "*.log",
  "deploy\*.key"
)

# Use Compress-Archive with Get-ChildItem filtered
$items = Get-ChildItem -Recurse -Force | Where-Object {
  $p = $_.FullName
  foreach ($ex in $excludes) {
    if ($ex -like "*\**") {
      # wildcard match (simple)
      if ($p -like $ex.Replace("*","*")) { return $false }
    } elseif ($p -like "*\$ex*") { return $false }
  }
  return $true
}

if (Test-Path $OutPath) { Remove-Item $OutPath }
Compress-Archive -Path $items -DestinationPath $OutPath -Force
Write-Host "Created $OutPath"
Write-Host "Remember: do not include .env in the archive. Use deploy/.env.example on the server and set environment variables there."