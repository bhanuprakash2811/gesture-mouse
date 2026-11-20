"""
Benchmark inference speed and latency for the gesture model.
"""
import time
import numpy as np
from src.gesture_cnn import GestureCNN


def benchmark_inference_speed(num_iterations=1000):
    """Measure FPS and latency."""
    print("Benchmarking Inference Speed...")
    print("="*60)
    
    # Create dummy landmarks
    class Landmark:
        def __init__(self):
            self.x = np.random.uniform(0, 1)
            self.y = np.random.uniform(0, 1)
            self.z = np.random.uniform(-0.1, 0.1)
    
    landmarks = [Landmark() for _ in range(21)]
    
    # Load model
    print("Loading model...")
    cnn = GestureCNN(model_path='models/gesture_cnn.h5')
    
    # Warmup
    print("Warming up...")
    for _ in range(10):
        cnn.predict(landmarks)
    
    # Benchmark
    print(f"Running {num_iterations} inference iterations...")
    start = time.time()
    for _ in range(num_iterations):
        cnn.predict(landmarks)
    end = time.time()
    
    total_time = end - start
    avg_latency = (total_time / num_iterations) * 1000  # ms
    fps = num_iterations / total_time
    
    print("\n" + "="*60)
    print("BENCHMARK RESULTS")
    print("="*60)
    print(f"Iterations:     {num_iterations}")
    print(f"Total Time:     {total_time:.2f}s")
    print(f"Avg Latency:    {avg_latency:.2f}ms")
    print(f"FPS:            {fps:.1f}")
    print("="*60)
    
    # Real-time performance assessment
    if fps >= 30:
        print("✓ Excellent: Real-time performance at 30+ FPS")
    elif fps >= 20:
        print("✓ Good: Acceptable for most real-time applications")
    elif fps >= 10:
        print("⚠ Fair: May have noticeable latency")
    else:
        print("✗ Poor: Significant latency expected")


if __name__ == '__main__':
    benchmark_inference_speed(num_iterations=1000)
