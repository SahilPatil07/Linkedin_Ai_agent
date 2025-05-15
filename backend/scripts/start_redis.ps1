# Start Redis server
$redisPath = "C:\Program Files\Redis\redis-server.exe"
if (Test-Path $redisPath) {
    Start-Process -FilePath $redisPath -NoNewWindow
    Write-Host "Redis server started successfully"
} else {
    Write-Host "Redis server not found at $redisPath"
    Write-Host "Please make sure Redis is installed correctly"
} 