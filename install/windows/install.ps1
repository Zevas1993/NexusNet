Set-ExecutionPolicy Bypass -Scope Process -Force

# Install Python if not present
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Installing Python..."
    Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe" -OutFile "python-installer.exe"
    Start-Process -Wait -FilePath "python-installer.exe" -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1"
    Remove-Item "python-installer.exe"
}

# Install dependencies
Write-Host "Installing dependencies..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

Write-Host "Installation complete! Run: python apps/api/main.py"
