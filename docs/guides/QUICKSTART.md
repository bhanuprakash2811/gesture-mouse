# Quick Start Guide

## Prerequisites

1. **Python 3.8+** installed
2. **Webcam** connected
3. **Microphone** (optional, for voice commands)
4. **C++ compiler and CMake** are optional and only needed for the native extension

## Installation Steps

### Step 1: Create Virtual Environment

```bash
python -m venv venv
```

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

**Note:** If PyAudio installation fails on Windows:
1. Download the appropriate wheel from https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
2. Install: `pip install PyAudio-0.2.11-cp39-cp39-win_amd64.whl` (adjust version)

### Step 3: Optional C++ Module

The `cpp/` directory is empty in this workspace, so skip the native build. The
original source archive is kept locally but excluded from the public repository.
The app can run using its Python implementation.

### Step 4: Train Model (or use pre-trained)

Generate synthetic model:
```bash
python -m scripts.training.train_model
```

Or collect real data first:
```bash
python -m scripts.training.collect_data
# Then train:
python -m scripts.training.train_model
```

### Step 5: Run the Application

**Bare-hand mode:**
```bash
python src/main.py --mode hand
```

**Glove mode:**
```bash
python src/main.py --mode glove
```

## Usage Tips

1. **Hand Detection**: Ensure good lighting and clear view of your hand
2. **Gestures**: 
   - Open hand = move cursor
   - Index finger = left click
   - Middle finger = right click
   - All fingers = scroll
   - Pinch (thumb+index) = drag
   - Thumbs up = exit
3. **Voice Commands**: Say clearly "left click", "right click", "scroll up", "scroll down", or "exit"
4. **Quit**: Press 'q' key or show thumbs up gesture

## Troubleshooting

### "Module not found" errors
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt` again

### Camera not working
- Check camera permissions
- Try different camera index in code

- The optional C++ source is not present in `cpp/`; use the Python fallback or restore the local source archive before building.

### Low accuracy
- Collect more training data
- Adjust gesture thresholds in code
- Ensure consistent lighting

## Next Steps

- Customize gesture definitions
- Adjust smoothing parameters
- Add more voice commands
- Improve CNN architecture

