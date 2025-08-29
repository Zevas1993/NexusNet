$ErrorActionPreference = "Stop"
Start-Process -FilePath python -ArgumentList "-m","uvicorn","app.main:app","--port","8001","--host","127.0.0.1" -PassThru | Tee-Object -Variable proc | Out-Null
Start-Sleep -Seconds 3
Invoke-WebRequest -Uri "http://127.0.0.1:8001/health" -UseBasicParsing | Out-Null
$body = '{"session_id":"smoke","messages":[{"role":"user","content":"ping"}]}'
Invoke-WebRequest -Uri "http://127.0.0.1:8001/chat" -Method Post -ContentType "application/json" -Body $body -UseBasicParsing | Out-Null
Stop-Process -Id $proc.Id -Force
Write-Output "Smoke OK"
