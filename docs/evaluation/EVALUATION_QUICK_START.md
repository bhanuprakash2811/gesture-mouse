# Gesture Mouse - Evaluation Quick Start Guide

## Overview

Your project now includes comprehensive evaluation tools to assess model performance and compare against other approaches.

---

## Quick Start Commands

### 1. **Compare Against Baseline Models** (5-10 minutes)
```bash
pip install scikit-learn matplotlib seaborn
python -m scripts.evaluation.evaluate_model
```

**Output:**
- `results/accuracy_comparison.png` - Bar chart comparing all models
- `results/metrics_comparison.png` - Detailed metrics comparison
- `results/confusion_matrices.png` - Confusion matrices for each model
- `results/evaluation_report.txt` - Detailed text report

**Models Compared:**
- Your CNN
- Random Forest
- SVM (Support Vector Machine)
- kNN (k-Nearest Neighbors)
- Decision Tree

---

### 2. **Compare with Rule-Based Baseline** (2 minutes)
```bash
python -m scripts.evaluation.compare_with_baseline
```

**Output:**
- Shows how your CNN compares to:
  - Simple rule-based gesture detection
  - Random classifier baseline
- Per-class accuracy breakdown
- Recommendations for improvement

---

### 3. **Benchmark Inference Speed** (2-3 minutes)
```bash
python -m scripts.evaluation.benchmark_speed
```

**Output:**
- **FPS** (Frames Per Second) - for real-time performance
- **Latency** in milliseconds - time for one inference
- Quality assessment (Excellent/Good/Fair/Poor)

**What it measures:**
- How fast can your model make predictions
- Whether it can run in real-time (need 20+ FPS for smooth interaction)

---

### 4. **Real-Time Gesture Testing** (Interactive)
```bash
python -m scripts.evaluation.test_gestures
```

**Controls:**
- `s` - Save statistics
- `c` - Clear statistics  
- `q` - Quit

**Output:**
- Live video with hand landmarks drawn
- Current gesture and confidence displayed
- Real-time FPS counter
- `results/testbed_statistics.txt` - Per-gesture statistics

**Tests:**
- Live hand detection accuracy
- Gesture recognition in real conditions
- Confidence levels for different gestures
- False positive/negative rates

---

## What Each Evaluation Measures

| Tool | Measures | Duration | Output |
|------|----------|----------|--------|
| `evaluate_model.py` | Classification accuracy vs other models | 5-10 min | PNG charts + TXT report |
| `compare_with_baseline.py` | Accuracy vs simple rules | 2 min | Console output |
| `benchmark_speed.py` | Inference speed (FPS, latency) | 2-3 min | Console output |
| `test_gestures.py` | Real-world performance with video | 5+ min | TXT statistics |

---

## Understanding the Results

### Accuracy Evaluation

Your CNN should achieve:
- **Baseline**: 16.67% (random guessing among 6 classes)
- **Good**: 85%+ accuracy
- **Excellent**: 95%+ accuracy

### Speed Evaluation

For smooth real-time interaction:
- **Excellent**: 30+ FPS
- **Good**: 20-30 FPS
- **Acceptable**: 15-20 FPS
- **Laggy**: <15 FPS

### Metrics Explanation

- **Accuracy**: Percentage of correct predictions overall
- **Precision**: Of gestures predicted as X, how many were actually X
- **Recall**: Of actual X gestures, how many did we catch
- **F1-Score**: Balance between precision and recall
- **ROC-AUC**: Measure of model's discrimination ability

### Confusion Matrix

Shows which gestures are confused:
- Diagonal = correct predictions
- Off-diagonal = misclassifications
- High values at (2,3) mean gesture 2 is often confused with gesture 3

---

## Step-by-Step Evaluation Plan

### Phase 1: Quick Assessment (15 minutes)
1. Run `evaluate_model.py` to see how your CNN compares
2. Run `benchmark_speed.py` to check if speed is acceptable

### Phase 2: Detailed Analysis (10 minutes)
1. Run `compare_with_baseline.py` to understand improvement over simple rules
2. Check `results/evaluation_report.txt` for detailed per-class performance

### Phase 3: Real-World Testing (15+ minutes)
1. Run `test_gestures.py` 
2. Perform various gestures in front of camera
3. Check `results/testbed_statistics.txt` for real-world accuracy

### Phase 4: Optimization (Optional)
- If accuracy is poor: Collect more training data, adjust model architecture
- If speed is poor: Use model quantization, C++ optimization
- If specific gestures fail: Add more training samples for those classes

---

## Interpreting the Comparison Charts

### Accuracy Comparison Chart
- Shows accuracy of each model
- Your CNN (green) should be higher than baselines (blue)
- Random Forest often provides good baseline performance

### Metrics Comparison Chart
- Shows 4 key metrics for each model
- Look for models that are high in all metrics
- Precision vs Recall tradeoff is common

### Confusion Matrices
- Darker blue = more predictions in that cell
- Diagonal should be darkest (correct predictions)
- Off-diagonal darkness reveals which gestures are confused

---

## Expected Results

### For Synthetic Data
```
Your CNN:          ~90-95% accuracy
Random Forest:     ~70-80% accuracy
SVM:               ~80-85% accuracy
kNN:               ~75-85% accuracy
Decision Tree:     ~70-80% accuracy
```

### For Real Data (After Training)
```
Your CNN:          ~85-92% accuracy
Random Forest:     ~65-75% accuracy
Others:            ~60-75% accuracy
```

### Speed Benchmark
```
FPS:               25-45 FPS (depending on hardware)
Latency:           22-40 ms per inference
```

---

## Advanced Customization

### Adjust Confidence Threshold
Edit `scripts/evaluation/test_gestures.py` line ~35:
```python
self.confidence_threshold = 0.6  # Change this value
```
- Lower (0.3): More detections, more false positives
- Higher (0.8): Fewer detections, more false negatives

### Test Different Model Architectures
Edit `src/gesture_cnn.py` to change the neural network:
```python
def build_model(self):
    # Add more layers, change activation functions, etc.
    self.model = keras.Sequential([
        layers.Dense(256, activation='relu', input_shape=input_shape),
        # Your custom architecture
    ])
```

### Compare with Your Own Baseline
Edit `compare_with_baseline.py` to implement custom heuristics

---

## Troubleshooting

### ImportError: No module named 'scikit-learn'
```bash
pip install scikit-learn matplotlib seaborn
```

### Model not found at 'models/gesture_cnn.h5'
```bash
python -m scripts.training.train_model  # Train the model first
```

### Slow performance
- Check `benchmark_speed.py` output
- Native optimization is unavailable until the local C++ source archive is restored.
- Use GPU if available: CUDA/cuDNN setup

### No webcam detected in `test_gestures.py`
- Verify webcam is connected
- Try different camera_index: 0, 1, 2, etc.

---

## Next Steps After Evaluation

### If Accuracy is Good (>85%)
1. Proceed with real-world deployment
2. Implement additional gestures
3. Add confidence-based filtering

### If Accuracy is Fair (70-85%)
1. Collect more diverse training data
2. Try different model architectures
3. Add data augmentation
4. Tune hyperparameters

### If Accuracy is Poor (<70%)
1. Inspect training data quality
2. Check hand tracking is working correctly
3. Try completely different architecture
4. Verify data preprocessing is correct

---

## Files Generated

After running evaluations, check:
- `results/accuracy_comparison.png`
- `results/metrics_comparison.png`
- `results/confusion_matrices.png`
- `results/evaluation_report.txt`
- `results/testbed_statistics.txt`

All results are timestamped and saved for comparison across runs.
