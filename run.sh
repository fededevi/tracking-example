#!/bin/bash

# Set default video file name
DEFAULT_VIDEO_FILE="input.mp4"

# Check if the video file exists, if not use the default name
VIDEO_FILE="${1:-$DEFAULT_VIDEO_FILE}"

# Install requirements
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Check if the video file exists
if [ ! -f "$VIDEO_FILE" ]; then
    echo "Error: $VIDEO_FILE does not exist."
    exit 1
fi

# Run the Python script with the video file
echo "Running the tracking script with $VIDEO_FILE..."
python3 main.py "$VIDEO_FILE" 0 400
