# Start Redis server
$redisPaths = @(
    "C:\Program Files\Redis\redis-server.exe",
    "C:\Redis\redis-server.exe",
    "${env:ProgramFiles}\Redis\redis-server.exe"
)

$redisStarted = $false
foreach ($path in $redisPaths) {
    if (Test-Path $path) {
        # Try to stop Redis gracefully first
        try {
            $redisProcess = Get-Process redis-server -ErrorAction SilentlyContinue
            if ($redisProcess) {
                $redisProcess | Stop-Process -Force -ErrorAction SilentlyContinue
                Start-Sleep -Seconds 2
            }
        } catch {
            Write-Host "Could not stop existing Redis process, continuing anyway..."
        }
        
        # Start Redis with config file
        Start-Process -FilePath $path -ArgumentList "C:\Redis\redis.windows.conf" -NoNewWindow
        Write-Host "Redis server started successfully from $path"
        $redisStarted = $true
        break
    }
}

if (-not $redisStarted) {
    Write-Host "Redis server not found. Please make sure Redis is installed correctly."
    Write-Host "You can download Redis for Windows from: https://github.com/microsoftarchive/redis/releases"
    exit 1
}

# Get Python path
$pythonPath = (Get-Command python).Path

# Start Celery worker
try {
    Start-Process -FilePath $pythonPath -ArgumentList "-m celery -A app.worker worker --loglevel=info" -NoNewWindow
    Write-Host "Celery worker started successfully"
} catch {
    Write-Host "Failed to start Celery worker. Please make sure Celery is installed: pip install celery"
    exit 1
}

# Start FastAPI server
try {
    Start-Process -FilePath $pythonPath -ArgumentList "-m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" -NoNewWindow
    Write-Host "FastAPI server started successfully"
} catch {
    Write-Host "Failed to start FastAPI server. Please make sure Uvicorn is installed: pip install uvicorn"
    exit 1
} 