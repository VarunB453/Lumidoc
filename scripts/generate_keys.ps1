# generate_keys.ps1 - Generate RSA key pair for JWT authentication (Windows)
# Usage: powershell -ExecutionPolicy Bypass -File scripts/generate_keys.ps1

$ErrorActionPreference = "Stop"

$KeysDir = Join-Path $PSScriptRoot "..\apps\server\keys"

Write-Host "Generating RSA key pair..." -ForegroundColor Cyan

if (-not (Test-Path $KeysDir)) {
    New-Item -ItemType Directory -Path $KeysDir -Force | Out-Null
}

$PrivateKeyPath = Join-Path $KeysDir "private.pem"
$PublicKeyPath = Join-Path $KeysDir "public.pem"

# Check if openssl is available
$openssl = Get-Command openssl -ErrorAction SilentlyContinue
if (-not $openssl) {
    Write-Host "ERROR: openssl not found in PATH." -ForegroundColor Red
    Write-Host "Install OpenSSL for Windows or use Git Bash (ships with openssl)." -ForegroundColor Yellow
    Write-Host "  winget install ShiningLight.OpenSSL" -ForegroundColor Yellow
    exit 1
}

# Generate 2048-bit RSA private key
openssl genrsa -out $PrivateKeyPath 2048
if ($LASTEXITCODE -ne 0) { throw "Failed to generate private key" }

# Extract public key
openssl rsa -in $PrivateKeyPath -pubout -out $PublicKeyPath
if ($LASTEXITCODE -ne 0) { throw "Failed to extract public key" }

Write-Host ""
Write-Host "Keys generated in $KeysDir" -ForegroundColor Green
Write-Host "  - private.pem (keep secret!)" -ForegroundColor Yellow
Write-Host "  - public.pem" -ForegroundColor White
