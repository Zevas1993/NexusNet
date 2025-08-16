$ErrorActionPreference = "Stop"
Write-Host "Setting up NexusNet via WSL..."
if (-not (Get-Command wsl -ErrorAction SilentlyContinue)) {
    Write-Host "Installing WSL..."
    wsl --install --distribution Ubuntu
    Write-Host "Please reboot and run this script again."
    exit
}
wsl -e bash -c "cd /mnt/c/$(pwd | ForEach-Object { $_ -replace ':', '' -replace '\\', '/' }) && chmod +x install/linux/install.sh && ./install/linux/install.sh"