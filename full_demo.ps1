# Full demo: start server, POST a motion event, GET alerts, then stop server
# Run in PowerShell with BypassSandbox (requires uvicorn in PATH)

# 1️⃣ Start FastAPI on port 8080 (background)
$uvicorn = Start-Process -FilePath uvicorn -ArgumentList "backend.app.main:app","--host","0.0.0.0","--port","8080" -PassThru

# Give the server a moment to start
Start-Sleep -Seconds 3

# 2️⃣ Send POST request
$payload = '{"device_id":"esp-cam-pir-01","motion":true}'
try {
    $postResp = Invoke-RestMethod -Uri "http://127.0.0.1:8080/api/sensors/pir/" -Method POST -ContentType "application/json" -Body $payload
    Write-Output "POST succeeded: $(ConvertTo-Json $postResp)"
} catch {
    Write-Output "POST error: $_"
}

# 3️⃣ Retrieve alerts list
try {
    $alerts = Invoke-RestMethod -Uri "http://127.0.0.1:8080/api/alerts/" -Method GET
    Write-Output "GET alerts succeeded: $(ConvertTo-Json $alerts)"
} catch {
    Write-Output "GET error: $_"
}

# 4️⃣ Stop the server
Stop-Process -Id $uvicorn.Id -Force
Write-Output "FastAPI server stopped"
