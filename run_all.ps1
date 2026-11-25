# run_all.ps1 – Start JEEVA GANGA FastAPI server and open UI

# Ensure script runs with admin rights for firewall rule
$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Host "⚠️ Please run this PowerShell script **as Administrator** to create the firewall rule."
    Write-Host "You can re‑run the script after elevating the window."
    exit 1
}

# Create firewall rule to allow inbound TCP 8080 (if it does not already exist)
if (-not (Get-NetFirewallRule -DisplayName "JEEVA_GANGA_8080" -ErrorAction SilentlyContinue)) {
    New-NetFirewallRule -DisplayName "JEEVA_GANGA_8080" -Direction Inbound -Protocol TCP -LocalPort 8080 -Action Allow | Out-Null
    Write-Host "✅ Firewall rule created."
} else {
    Write-Host "✅ Firewall rule already exists."
}

# Kill any existing uvicorn process (ignore errors)
Get-Process uvicorn -ErrorAction SilentlyContinue | Stop-Process -Force

# Small pause to let the port free up
Start-Sleep -Seconds 2

# Activate virtual environment
$venvActivate = Join-Path $PSScriptRoot ".venv\Scripts\Activate.ps1"
if (Test-Path $venvActivate) {
    & $venvActivate
} else {
    Write-Error "Virtual environment not found at $venvActivate"
    exit 1
}

# Start FastAPI server in background, redirect output to separate log files
$stdoutLog = Join-Path $PSScriptRoot "server_stdout.log"
$stderrLog = Join-Path $PSScriptRoot "server_stderr.log"
Start-Process -FilePath "uvicorn" -ArgumentList @("backend.app.main:app","--host","0.0.0.0","--port","8080") -RedirectStandardOutput $stdoutLog -RedirectStandardError $stderrLog -NoNewWindow
Write-Host "🚀 FastAPI server started (logs: $stdoutLog, $stderrLog)"

# Give server a moment to start
Start-Sleep -Seconds 3

# Determine LAN IP (first IPv4 not loopback and up)
$lanIP = (Get-NetIPAddress -AddressFamily IPv4 |
    Where-Object { $_.InterfaceOperationalStatus -eq "Up" -and $_.IPAddress -notmatch "^127\." } |
    Select-Object -First 1 -ExpandProperty IPAddress)

# URLs to open
$localUrl = "http://127.0.0.1:8080/"
$lanUrl = if ($lanIP) { "http://$lanIP:8080/" } else { $null }

# Open URLs in default browser
Start-Process $localUrl
if ($lanUrl) { Start-Process $lanUrl }

# ESP‑CAM stream URL (adjust if different)
$espCamUrl = "http://192.168.163.69/"

# Sidecar link for interactive viewer (will appear in console)
Write-Host "\nSidecar link (click to open viewer): sidecar://$espCamUrl\n"

# Keep script alive until user stops it (optional)
Write-Host "Server is running. Press Ctrl+C to stop."
while ($true) { Start-Sleep -Seconds 60 }
