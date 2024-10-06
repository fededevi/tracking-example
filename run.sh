#!/bin/bash

# Set default video file name
DEFAULT_VIDEO_FILE="input.mp4"

# Check if the video file exists, if not use the default name
VIDEO_FILE="${1:-$DEFAULT_VIDEO_FILE}"

# Function to install Python 3 if not installed
install_python() {
    echo "Python 3 is not installed. Installing Python 3..."
    sudo apt update
    sudo apt install -y python3 python3-pip
}

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    install_python
fi

# Check if pip is installed
if ! command -v pip &> /dev/null; then
    echo "Pip is not installed. Installing pip..."
    sudo apt install -y python3-pip
fi

# Check if requirements are already installed
if ! pip freeze | grep -q -f requirements.txt; then
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
else
    echo "Python dependencies are already installed."
fi

# Check if the video file exists
if [ ! -f "$VIDEO_FILE" ]; then
    echo "Error: $VIDEO_FILE does not exist."
    exit 1
fi

# Run the Python script with the video file
echo "Running the tracking script with $VIDEO_FILE..."
python3 main.py "$VIDEO_FILE" 0 410
