# Installation Requirements for Evaluation Tools

The evaluation tools require additional dependencies beyond your base project.

## Quick Install

```bash
pip install scikit-learn matplotlib seaborn
```

That's it! These packages add:
- **scikit-learn**: Machine learning models (Random Forest, SVM, kNN, Decision Tree)
- **matplotlib**: Chart generation
- **seaborn**: Enhanced visualizations

## Complete Requirements

### Base Project (already have)
```
opencv-python>=4.8.0
mediapipe>=0.10.0
tensorflow>=2.13.0
numpy>=1.24.0
pyautogui>=0.9.54
SpeechRecognition>=3.10.0
pyaudio>=0.2.13
```

### For Evaluation Tools (NEW)
```
scikit-learn>=1.3.0
matplotlib>=3.7.0
seaborn>=0.12.0
```

## Installation Command

```bash
# Install evaluation dependencies
pip install scikit-learn matplotlib seaborn

# Or install all at once
pip install scikit-learn matplotlib seaborn opencv-python mediapipe tensorflow numpy pyautogui SpeechRecognition
```

## Verification

Check installation:

```bash
python -c "import sklearn, matplotlib, seaborn; print('✓ All packages installed')"
```

Expected output:
```
✓ All packages installed
```

## If Installation Fails

### For Windows
```bash
pip install --upgrade pip
pip install scikit-learn matplotlib seaborn
```

### For Mac/Linux
```bash
python3 -m pip install --upgrade pip
python3 -m pip install scikit-learn matplotlib seaborn
```

### For Virtual Environment
```bash
# Activate your venv first
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Then install
pip install scikit-learn matplotlib seaborn
```

## Disk Space Required

- scikit-learn: ~100 MB
- matplotlib: ~50 MB
- seaborn: ~5 MB
- **Total: ~155 MB**

Ensure you have at least 200 MB free space.

## Optional: GPU Support

For faster model training (optional):

```bash
pip install tensorflow[and-cuda]
```

Note: GPU installation is more complex. CPU is fine for evaluation.

## Troubleshooting

### ImportError: No module named 'sklearn'
```bash
pip install scikit-learn
```

### ImportError: No module named 'matplotlib'
```bash
pip install matplotlib
```

### ImportError: No module named 'seaborn'
```bash
pip install seaborn
```

### Permission Denied (Mac/Linux)
```bash
sudo pip install scikit-learn matplotlib seaborn
```

Or use:
```bash
pip install --user scikit-learn matplotlib seaborn
```

## Next Steps

After installing dependencies:

```bash
python -m scripts.evaluation.compare_with_baseline  # Start with this (2 min)
```

## Done! ✅

You're ready to evaluate your gesture mouse model!
