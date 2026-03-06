# Quick Setup Script for Spotify Integration
# Run this in PowerShell

Write-Host "🎵 Spotify Integration Setup" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""

# Check if spotipy is installed
Write-Host "Checking dependencies..." -ForegroundColor Yellow
try {
    python -c "import spotipy" 2>$null
    Write-Host "✅ spotipy installed" -ForegroundColor Green
} catch {
    Write-Host "❌ spotipy not found. Installing..." -ForegroundColor Red
    pip install spotipy requests
}

Write-Host ""
Write-Host "📝 Next Steps:" -ForegroundColor Cyan
Write-Host "1. Go to: https://developer.spotify.com/dashboard" -ForegroundColor White
Write-Host "2. Create a new app (it's free!)" -ForegroundColor White
Write-Host "3. Copy your Client ID and Client Secret" -ForegroundColor White
Write-Host ""

# Prompt for credentials
Write-Host "Enter your Spotify credentials:" -ForegroundColor Yellow
$clientId = Read-Host "Client ID"
$clientSecret = Read-Host "Client Secret" -AsSecureString
$clientSecretPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($clientSecret)
)

# Set environment variables for current session
$env:SPOTIFY_CLIENT_ID = $clientId
$env:SPOTIFY_CLIENT_SECRET = $clientSecretPlain

Write-Host ""
Write-Host "✅ Environment variables set for this session!" -ForegroundColor Green
Write-Host ""

# Create .streamlit directory and secrets file
$streamlitDir = ".streamlit"
$secretsFile = "$streamlitDir\secrets.toml"

if (!(Test-Path $streamlitDir)) {
    New-Item -ItemType Directory -Path $streamlitDir -Force | Out-Null
    Write-Host "✅ Created .streamlit directory" -ForegroundColor Green
}

# Create secrets.toml
$secretsContent = @"
# Spotify API Credentials
SPOTIFY_CLIENT_ID = "$clientId"
SPOTIFY_CLIENT_SECRET = "$clientSecretPlain"
"@

Set-Content -Path $secretsFile -Value $secretsContent
Write-Host "✅ Created secrets.toml file" -ForegroundColor Green

# Add to .gitignore
$gitignoreFile = ".gitignore"
if (!(Test-Path $gitignoreFile)) {
    New-Item -ItemType File -Path $gitignoreFile | Out-Null
}

$gitignoreContent = Get-Content $gitignoreFile -ErrorAction SilentlyContinue
if ($gitignoreContent -notcontains ".streamlit/secrets.toml") {
    Add-Content -Path $gitignoreFile -Value "`n# Streamlit secrets`n.streamlit/secrets.toml"
    Write-Host "✅ Added secrets.toml to .gitignore" -ForegroundColor Green
}

Write-Host ""
Write-Host "🚀 Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "To run the app:" -ForegroundColor Cyan
Write-Host "  cd FRONTEND" -ForegroundColor White
Write-Host "  streamlit run app_with_spotify.py" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  Note: Preview playback works for FREE Spotify accounts!" -ForegroundColor Yellow
Write-Host "    Full playback control requires Spotify Premium." -ForegroundColor Yellow
Write-Host ""
