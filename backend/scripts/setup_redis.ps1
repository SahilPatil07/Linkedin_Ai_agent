# Run as Administrator
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Warning "Please run this script as Administrator!"
    exit
}

# Create Redis directory if it doesn't exist
$redisPath = "C:\Redis"
if (-not (Test-Path $redisPath)) {
    New-Item -ItemType Directory -Force -Path $redisPath
    Write-Host "Created Redis directory at $redisPath"
}

# Add Redis to PATH
$currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
if (-not $currentPath.Contains($redisPath)) {
    [Environment]::SetEnvironmentVariable("Path", $currentPath + ";$redisPath", "Machine")
    Write-Host "Added Redis to system PATH"
}

# Create Redis configuration
$redisConfig = @"
port 6379
bind 127.0.0.1
maxmemory 100mb
maxmemory-policy allkeys-lru
"@

$redisConfig | Out-File -FilePath "$redisPath\redis.windows.conf" -Encoding ASCII
Write-Host "Created Redis configuration file"

Write-Host "Redis setup completed. Please make sure to:"
Write-Host "1. Download Redis-x64-3.0.504.zip from https://github.com/microsoftarchive/redis/releases"
Write-Host "2. Extract all files to C:\Redis"
Write-Host "3. Restart your PowerShell window"
Write-Host "4. Run .\scripts\start_services.ps1" 