# Model Comparison Quick Reference

## All Models at a Glance

```
┌────────────────────────────────────────────────────────────────────────────────┐
│                    GESTURE RECOGNITION MODEL COMPARISON                        │
├─────────────────┬──────────┬──────────┬───────────┬──────────┬────────────────┤
│ Model           │ Accuracy │ Speed    │ Training  │ Memory   │ Best For       │
├─────────────────┼──────────┼──────────┼───────────┼──────────┼────────────────┤
│ Your CNN        │ 90-95%   │ 30+ FPS  │ 10 min    │ 5 MB     │ Real-time apps │
│ Random Forest   │ 70-80%   │ 20 FPS   │ 1 min     │ 20 MB    │ Quick baseline │
│ SVM             │ 80-85%   │ 15 FPS   │ 2 min     │ 10 MB    │ Classification │
│ kNN (k=5)       │ 75-85%   │ 10 FPS   │ <1 sec    │ 50 MB    │ Simple cases   │
│ Decision Tree   │ 70-80%   │ 25 FPS   │ 1 min     │ 2 MB     │ Interpretable  │
└─────────────────┴──────────┴──────────┴───────────┴──────────┴────────────────┘
```

## What to Use For What

### Want Highest Accuracy?
→ **Your CNN** (90-95%)

### Want Fastest Training?
→ **kNN** (<1 second) but slower inference

### Want Best Real-Time Performance?
→ **Your CNN** (30+ FPS) or Decision Tree (25+ FPS)

### Want Most Interpretable?
→ **Decision Tree** (can visualize decision path)

### Want Good All-Around Baseline?
→ **Random Forest** (balanced, quick to train)

---

## Evaluation Tools Comparison

```
┌─────────────────────────────────┬────────┬──────────┬────────────────────────┐
│ Tool                            │ Time   │ Metrics  │ Output                 │
├─────────────────────────────────┼────────┼──────────┼────────────────────────┤
│ evaluate_model.py               │ 10 min │ 5 models │ Charts + Report        │
│ compare_with_baseline.py         │ 2 min  │ 3 comps  │ Console only           │
│ benchmark_speed.py              │ 2 min  │ FPS/ms   │ Console only           │
│ test_gestures.py                │ 15 min │ Real-world│ Video + Statistics    │
└─────────────────────────────────┴────────┴──────────┴────────────────────────┘
```

---

## Quick Evaluation Decision Tree

```
┌─ START ─────────────────────────────────────────────────────┐
│                                                               │
│  ┌─ Time: 5 minutes?                                         │
│  │  YES → benchmark_speed.py + compare_with_baseline.py    │
│  │  NO  → Next question                                     │
│  │                                                            │
│  ┌─ Time: 15 minutes?                                        │
│  │  YES → evaluate_model.py (full comparison)               │
│  │  NO  → Next question                                     │
│  │                                                            │
│  ┌─ Time: 20+ minutes?                                       │
│  │  YES → test_gestures.py (real-world testing)             │
│  │  NO  → Run them all together in background              │
│  │                                                            │
└─────────────────────────────────────────────────────────────┘
```

---

## Performance Benchmarks

### Accuracy Levels

| Level | Accuracy | Quality | Example Use |
|-------|----------|---------|------------|
| 🟢 Excellent | 95%+ | Production-ready | Google MediaPipe |
| 🟢 Good | 85-94% | Daily use | Your CNN (likely) |
| 🟡 Fair | 75-84% | Acceptable | Random Forest |
| 🟠 Poor | 65-74% | Needs work | kNN on small data |
| 🔴 Bad | <65% | Not usable | Random classifier |

### Speed Levels

| Level | FPS | Latency | Usability |
|-------|-----|---------|-----------|
| 🟢 Excellent | 30+ | <35ms | Smooth, responsive |
| 🟢 Good | 20-29 | 35-50ms | Good for most apps |
| 🟡 Fair | 15-19 | 50-70ms | Noticeable delay |
| 🟠 Poor | 10-14 | 70-100ms | Frustrating |
| 🔴 Bad | <10 | 100+ | Not usable |

---

## Reading Confusion Matrix

### Example (Good Model):
```
Predicted:
       MC   LC   RC   SC   DR   TU
MC  [950   0    0    0    0    0  ]  ← Most correct
LC  [  0  945   5    0    0    0  ]
RC  [  0    3  940   0    2    0  ]
SC  [  0    0    0  955   0    0  ]
DR  [  0    0    2    0  943   0  ]
TU  [  0    0    0    0    5  950  ]
```
Diagonal is high = Good!

### Example (Confusing Model):
```
Predicted:
       MC   LC   RC   SC   DR   TU
MC  [700  150  50   0    0    0  ]  ← Confused!
LC  [100  600  200  0    0    0  ]
RC  [ 50  180  620  0    0    0  ]
SC  [  0    0    0  800  100  100]
DR  [  0    0    0   50  850  100]
TU  [  0    0    0  100  100  800]
```
Off-diagonal is high = Confusing classes!

**Legend:**
- MC = move_cursor
- LC = left_click
- RC = right_click
- SC = scroll
- DR = drag
- TU = thumbs_up

---

## Which Model Comparison to Run?

### Scenario 1: Just want to know if my model is good
```bash
python -m scripts.evaluation.compare_with_baseline  # 2 minutes
```
Quick answer: Does my CNN beat random guessing and simple rules?

### Scenario 2: Want to pick the best model for deployment
```bash
python -m scripts.evaluation.evaluate_model  # 10 minutes
```
Full comparison of 5 different models on your data.

### Scenario 3: Want to know if it's fast enough
```bash
python -m scripts.evaluation.benchmark_speed  # 2 minutes
```
FPS and latency for real-time usage.

### Scenario 4: Want to validate real-world performance
```bash
python -m scripts.evaluation.test_gestures  # 15+ minutes
```
Live testing with your hand and camera.

### Scenario 5: Want the complete picture
```bash
# Run all in sequence (30 minutes total)
python -m scripts.evaluation.compare_with_baseline
python -m scripts.evaluation.benchmark_speed
python -m scripts.evaluation.evaluate_model
python -m scripts.evaluation.test_gestures
```

---

## Expected Results from Each Tool

### evaluate_model.py Output
```
============================================================
CNN Model Performance:
  Accuracy:  0.9432
  Precision: 0.9425
  Recall:    0.9432
  F1-Score:  0.9427

Per-class breakdown:
  move_cursor     - P: 0.953, R: 0.948, F1: 0.950
  left_click      - P: 0.942, R: 0.945, F1: 0.943
  ...
============================================================
```

### compare_with_baseline.py Output
```
============================================================
ACCURACY COMPARISON
============================================================
Your CNN Model:         93.50%
Rule-Based Baseline:    68.20%
Random Classifier:      16.67%
============================================================

Improvement:
  vs Rule-Based:  +25.30%
  vs Random:      +76.83%
```

### benchmark_speed.py Output
```
============================================================
BENCHMARK RESULTS
============================================================
Iterations:     1000
Total Time:     32.45s
Avg Latency:    32.45ms
FPS:            30.8

✓ Excellent: Real-time performance at 30+ FPS
```

### test_gestures.py Output (saved to results/testbed_statistics.txt)
```
Total Recognitions: 523

Gesture Distribution:
  move_cursor    :  156 (29.8%)
  left_click     :  98  (18.7%)
  right_click    :  87  (16.6%)
  scroll         :  93  (17.8%)
  drag           :  65  (12.4%)
  thumbs_up      :  24  (4.6%)

Average Confidence per Gesture:
  move_cursor    : Avg=0.876, Min=0.623, Max=0.998
  left_click     : Avg=0.834, Min=0.512, Max=0.997
  ...
```

---

## Troubleshooting Your Evaluation

| Problem | Cause | Solution |
|---------|-------|----------|
| ImportError: sklearn | Missing package | `pip install scikit-learn` |
| Model not found | Didn't train yet | `python -m scripts.training.train_model` |
| Slow FPS | Model is slow | Run `benchmark_speed.py` for diagnosis |
| Low accuracy | Bad training data | Collect real gesture data |
| Specific gesture fails | Confused classes | Check confusion matrix |
| No webcam found | Camera not available | Try different camera_index |

---

## Final Checklist

- [ ] Run `evaluate_model.py` and check accuracy
- [ ] Run `benchmark_speed.py` and verify FPS > 20
- [ ] Run `test_gestures.py` with your hand
- [ ] Check `results/` directory for visualizations
- [ ] Review confusion matrix for confusing classes
- [ ] If accuracy < 85%, collect more training data
- [ ] If speed < 20 FPS, try C++ optimization
- [ ] Deploy with confidence! 🚀

---

**Your gesture mouse is ready for evaluation!**

Pick a tool above and start comparing. The complete evaluation takes 30 minutes and gives you full confidence in your model.
