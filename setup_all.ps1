# Setup_All.ps1 - Run all setup steps for JEEVA GANGA project
# ---------------------------------------------------------------
# 1. Install backend dependencies and start backend server
# ---------------------------------------------------------------
Set-Location "C:\Users\DELL\Desktop\JEEVA_GANGA\backend"
Write-Host "Installing backend dependencies..."
npm install
Write-Host "Starting backend as detached process..."
Start-Process -FilePath "cmd.exe" -ArgumentList "/c npm start" -WorkingDirectory (Get-Location) -NoNewWindow
# Give backend time to bind
Start-Sleep -Seconds 5

# ---------------------------------------------------------------
# 2. Install frontend dependencies and start dev server
# ---------------------------------------------------------------
Set-Location "C:\Users\DELL\Desktop\JEEVA_GANGA\frontend"
Write-Host "Installing frontend dependencies..."
npm install
Write-Host "Starting frontend dev server as detached process..."
Start-Process -FilePath "cmd.exe" -ArgumentList "/c npm run dev" -WorkingDirectory (Get-Location) -NoNewWindow
# Give frontend time to start
Start-Sleep -Seconds 5

# ---------------------------------------------------------------
# 3. Detect PC LAN IP (fallback to manual entry if detection fails)
# ---------------------------------------------------------------
$pcIp = (Get-NetIPConfiguration |
    Where-Object { $_.IPv4DefaultGateway -ne $null } |
    Select-Object -ExpandProperty IPv4Address |
    Select-Object -First 1).IPAddress
if (-not $pcIp) {
    # Manually set your LAN IP here if auto‑detect failed
    $pcIp = "192.168.1.42"  # <--- replace with your PC's LAN address
    Write-Host "Auto‑detect failed – using manual IP $pcIp"
} else {
    Write-Host "Detected PC LAN IP: $pcIp"
}

# ---------------------------------------------------------------
# 4. POST camera URL to backend
# ---------------------------------------------------------------
$cameraUrl = "http://192.168.163.69"   # <-- replace if your ESP‑Cam uses a different address/port
$backendUrl = "http://$pcIp:4000/api/cam"
Write-Host "Posting camera URL to $backendUrl"
Invoke-RestMethod -Method Post -Uri $backendUrl -ContentType "application/json" -Body ('{"url":"' + $cameraUrl + '"}')

# ---------------------------------------------------------------
# 5. Verify backend state
# ---------------------------------------------------------------
Write-Host "Verifying backend state..."
$state = Invoke-RestMethod -Method Get -Uri "http://localhost:4000/api/state" -UseBasicParsing
Write-Host "Backend state:`n$(ConvertTo-Json $state -Depth 3)"

# ---------------------------------------------------------------
# 6. Open the Camera page in default browser
# ---------------------------------------------------------------
$cameraPage = "http://localhost:5173/camera"
Write-Host "Opening camera page $cameraPage"
Start-Process $cameraPage

# ---------------------------------------------------------------
# Done – you should now see the live ESP‑Cam stream in the web UI.
# ---------------------------------------------------------------
