# Gesture Controlled Virtual Mouse

A contactless Human-Computer Interaction (HCI) system that replaces the physical mouse using hand gestures and voice commands.

[Quick start](docs/guides/QUICKSTART.md) · [Project walkthrough](docs/guides/PROJECT_SUMMARY.md) · [Documentation index](docs/README.md) · [Evaluation guides](docs/evaluation/DOCUMENTATION_INDEX.md)

## Features

- **Bare-hand gesture tracking** using MediaPipe (21 landmark hand-tracking)
- **Colored glove gesture tracking** using OpenCV color detection
- **CNN-based gesture classification** for 6 gesture types
- **Voice command recognition** using SpeechRecognition + PyAudio
- **Smooth mouse control** with exponential moving average smoothing
- **Optional C++ optimization support** via PyBind11 (native source is kept locally, not included in the repository)
- **Multiple interaction modes**: cursor movement, left/right click, scroll, drag & drop

## Gesture Classes

1. **move_cursor** - Open hand for cursor movement
2. **left_click** - Index finger extended
3. **right_click** - Middle finger extended
4. **scroll** - All fingers extended
5. **drag** - Thumb and index finger pinch
6. **thumbs_up** - Exit gesture

## Voice Commands

- "left click"
- "right click"
- "scroll up"
- "scroll down"
- "exit" / "quit" / "stop"

## System Requirements

- Python 3.8+
- Windows 10/11 (or Linux/macOS with modifications)
- Webcam
- Microphone (for voice commands)
- C++ compiler and CMake are needed only for the optional native extension

## Installation

### 1. Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux/macOS
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

**Note for PyAudio on Windows:**
If PyAudio installation fails, download the appropriate wheel from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio) and install:
```bash
pip install PyAudio-0.2.11-cp39-cp39-win_amd64.whl  # Adjust version
```

### 3. Optional C++ Module

The `cpp/` directory is empty in this workspace, so the optional C++ module cannot
currently be built. The original C++ archive is kept locally but excluded from
the public repository because of its size. The Python application remains usable
without the module.

### 4. Train CNN Model (Optional)

If you don't have a pre-trained model, generate one:

```bash
python -m scripts.training.train_model
```

This will create `models/gesture_cnn.h5` with synthetic data. For better accuracy, collect real data:

```bash
python -m scripts.training.collect_data
```

Then retrain:
```bash
python -m scripts.training.train_model
```

## Docker on Windows

Docker Desktop for Windows runs this project in a Linux container. Use the
container for dependency checks, unit tests, model training, and evaluation:

```powershell
docker compose build
docker compose run --rm gesture-mouse
docker compose run --rm gesture-mouse xvfb-run -a python -m unittest discover -s tests -v
docker compose run --rm gesture-mouse python -m scripts.training.train_model
docker compose run --rm gesture-mouse python -m scripts.evaluation.evaluate_model
```

The `data/`, `models/`, and `results/` folders are mounted from the project,
so datasets, trained models, and reports are available on Windows after a
container exits. To use the webcam, OpenCV window, microphone, and Windows
mouse, launch the interactive app natively with `run.bat` after installing the
Python dependencies on the host. Docker Desktop does not provide these Windows
desktop devices to this Linux container through the included Compose setup.

## Usage

### Run with Bare-hand Mode (MediaPipe)

```bash
python src/main.py --mode hand
```

### Run with Glove Mode (OpenCV Color Detection)

```bash
python src/main.py --mode glove
```

### Specify Custom Model

```bash
python src/main.py --mode hand --model models/my_model.h5
```

## Controls

- **Q key**: Quit application
- **Voice commands**: Say "left click", "right click", "scroll up", "scroll down", or "exit"
- **Gestures**: Show gestures to camera (see Gesture Classes above)

## Project Structure

```
gesture_mouse/
├── src/                     # Application package and runtime modules
├── scripts/
│   ├── training/            # Data collection and model training
│   ├── evaluation/          # Model comparison and live evaluation
│   └── maintenance/         # Installation checks
├── tests/                   # Unit tests
├── docs/
│   ├── guides/              # Setup and project walkthroughs
│   └── evaluation/          # Evaluation references and reports
├── cpp/                     # Optional C++ extension location
├── data/                    # Datasets
├── models/                  # Trained models
├── results/                 # Evaluation outputs
├── screenshots/             # Project screenshots
├── requirements.txt         # Python dependencies
└── README.md                # Start here
```

## How It Works

1. **Camera Input**: Captures video frames from webcam
2. **Hand Detection**: 
   - Bare-hand: MediaPipe detects 21 hand landmarks
   - Glove: OpenCV detects colored glove and tracks centroid
3. **Feature Extraction**: Extracts features from landmarks (distances, angles)
4. **Gesture Classification**: CNN classifies gesture from features
5. **Voice Processing**: Background thread listens for voice commands
6. **Action Mapping**: Maps gesture/voice command to mouse action
7. **Mouse Control**: Executes action with smoothing to reduce jitter

## Performance Optimization

- **Optional C++ module**: The native source archive is preserved but not extracted; the current workspace runs without it.
- **Exponential Moving Average**: Smooths cursor movement
- **Gesture Cooldown**: Prevents rapid repeated actions
- **Efficient CNN**: Lightweight architecture for real-time inference

## Troubleshooting

### Camera not detected
- Check camera permissions
- Try different camera index: Modify `camera_index` in `hand_tracking.py`

### Voice commands not working
- Check microphone permissions
- Install PyAudio correctly (see Installation section)
- Test microphone with system settings

### Model not found
- Run `python -m scripts.training.train_model` to generate model
- Or download pre-trained model to `models/gesture_cnn.h5`

### C++ module import error
- The optional C++ source is not present in `cpp/`; continue using the Python fallback, or restore the local source archive before building.

### Low FPS
- Reduce camera resolution in `hand_tracking.py`
- Use GPU-accelerated TensorFlow
- Close other applications

## Training Your Own Model

1. **Collect Data**: Run `python -m scripts.training.collect_data` and record samples for each gesture
2. **Train Model**: Run `python -m scripts.training.train_model` to train CNN
3. **Evaluate**: Check validation accuracy in training output
4. **Improve**: Collect more diverse data for better accuracy

## Future Enhancements

- Multi-hand support
- Custom gesture definitions
- Machine learning-based gesture recognition improvements
- Support for more mouse actions (middle click, double click)
- Configuration file for customization
- GUI for settings and calibration

## License

This project is provided as-is for educational and research purposes.

## Acknowledgments

- MediaPipe for hand tracking
- TensorFlow/Keras for CNN implementation
- PyBind11 for Python-C++ integration
- OpenCV for computer vision operations

