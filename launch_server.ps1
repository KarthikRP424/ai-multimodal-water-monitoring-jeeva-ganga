# launch_server.ps1 – start JEEVA GANGA FastAPI server (non‑blocking)

# ----------------------------------------------------------------
# Ensure firewall rule exists (run as admin once; subsequent runs are safe)
if (-not (Get-NetFirewallRule -DisplayName "JEEVA_GANGA_8080" -ErrorAction SilentlyContinue)) {
    try {
        New-NetFirewallRule -DisplayName "JEEVA_GANGA_8080" -Direction Inbound -Protocol TCP -LocalPort 8080 -Action Allow | Out-Null
        Write-Host "✅ Firewall rule created."
    } catch {
        Write-Warning "Failed to create firewall rule – you may need to run this script as Administrator."
    }
} else {
    Write-Host "✅ Firewall rule already exists."
}

# ----------------------------------------------------------------
# Kill any existing uvicorn process (ignore errors)
Get-Process uvicorn -ErrorAction SilentlyContinue | Stop-Process -Force

# ----------------------------------------------------------------
# Activate virtual environment
$venvActivate = Join-Path $PSScriptRoot ".venv\Scripts\Activate.ps1"
if (Test-Path $venvActivate) {
    & $venvActivate
} else {
    Write-Error "Virtual environment not found at $venvActivate"
    exit 1
}

# ----------------------------------------------------------------
# Prepare log files
$stdoutLog = Join-Path $PSScriptRoot "server_stdout.log"
$stderrLog = Join-Path $PSScriptRoot "server_stderr.log"

# Path to uvicorn inside the venv
$uvicornExe = Join-Path $PSScriptRoot ".venv\Scripts\uvicorn.exe"

# ----------------------------------------------------------------
# **START THE SERVER** – single line, all args together
Start-Process -FilePath $uvicornExe `
    -ArgumentList @("backend.app.main:app","--host","0.0.0.0","--port","8080") `
    -RedirectStandardOutput $stdoutLog `
    -RedirectStandardError $stderrLog `
    -WindowStyle Hidden

Write-Host "🚀 FastAPI server started (logs: $stdoutLog, $stderrLog)"

# ----------------------------------------------------------------
# Show the LAN URL for easy testing
$lanIP = (Get-NetIPAddress -AddressFamily IPv4 |
    Where-Object { $_.InterfaceOperationalStatus -eq "Up" -and $_.IPAddress -notmatch "^127\." } |
    Select-Object -First 1 -ExpandProperty IPAddress)

if ($lanIP) { Write-Host "Open this URL on any device on the LAN: http://$lanIP:8080/" }

# ----------------------------------------------------------------
# Keep PowerShell alive until you press Ctrl+C (optional)
Write-Host "Server is running. Press Ctrl+C to stop."
while ($true) { Start-Sleep -Seconds 60 }
