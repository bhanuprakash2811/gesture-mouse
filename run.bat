@echo off
REM Quick run script for Windows
echo Starting Gesture Controlled Virtual Mouse...

REM Check if virtual environment exists
if not exist venv (
    echo Virtual environment not found. Creating...
    python -m venv venv
    echo Installing dependencies...
    venv\Scripts\pip install -r requirements.txt
)

REM Activate virtual environment
call venv\Scripts\activate



REM Check if model exists
if not exist models\gesture_cnn.h5 (
    echo Model not found. Training model...
    python -m scripts.training.train_model
)

REM Run the application
python src/main.py --mode hand

pause
