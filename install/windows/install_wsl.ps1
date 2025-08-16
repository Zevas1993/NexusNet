Set-ExecutionPolicy Bypass -Scope Process -Force

Write-Host "Setting up WSL for NexusNet..."

# Enable WSL
wsl --install

Write-Host "Please reboot and run: wsl -d Ubuntu -- bash -c 'cd /mnt/c/path/to/nexusnet && ./install/linux/install.sh'"
Write-Host "Replace /mnt/c/path/to/nexusnet with your actual path"
