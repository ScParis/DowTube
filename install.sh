#!/bin/bash

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

# Install ffmpeg if not already installed
if ! command -v ffmpeg &> /dev/null; then
    echo "Installing ffmpeg..."
    if [ -f /etc/debian_version ]; then
        sudo apt-get update
        sudo apt-get install -y ffmpeg
    elif [ -f /etc/redhat-release ]; then
        sudo dnf install -y ffmpeg
    elif [ -f /etc/arch-release ]; then
        sudo pacman -S --noconfirm ffmpeg
    else
        echo "Please install ffmpeg manually for your distribution"
    fi
fi

echo "Installation complete!"
