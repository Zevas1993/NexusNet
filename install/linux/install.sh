#!/bin/bash
set -e

echo "Installing NexusNet on Linux..."

# Install Python if not present
if ! command -v python3 &> /dev/null; then
    echo "Installing Python..."
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv
fi

# Install dependencies
echo "Installing dependencies..."
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt

echo "Installation complete! Run: python3 apps/api/main.py"
