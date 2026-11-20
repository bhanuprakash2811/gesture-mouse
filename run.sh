#!/bin/bash
# Quick run script for Linux/macOS

echo "Starting Gesture Controlled Virtual Mouse..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating..."
    python3 -m venv venv
    echo "Installing dependencies..."
    venv/bin/pip install -r requirements.txt
fi

# Activate virtual environment
source venv/bin/activate

# Check if model exists
if [ ! -f "models/gesture_cnn.h5" ]; then
    echo "Model not found. Training model..."
    python -m scripts.training.train_model
fi

# Run the application
python src/main.py --mode hand

