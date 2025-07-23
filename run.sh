#!/bin/bash
# Image Optimizer Launcher Script for macOS/Linux

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if virtual environment exists
if [ -d "$SCRIPT_DIR/.venv" ]; then
    echo "Using virtual environment..."
    PYTHON_CMD="$SCRIPT_DIR/.venv/bin/python"
else
    echo "Virtual environment not found, using system Python..."
    PYTHON_CMD="python3"
fi

# Run the image optimizer
echo "Starting Image Optimizer..."
$PYTHON_CMD "$SCRIPT_DIR/image_optimizer.py"
