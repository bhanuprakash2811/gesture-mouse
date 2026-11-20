"""
Training script for gesture CNN model.
Generates synthetic data or loads from dataset.
"""
import numpy as np
import tensorflow as tf
from tensorflow import keras
from src.gesture_cnn import GestureCNN, create_training_data_from_landmarks
import os
import pickle


def generate_synthetic_data(num_samples_per_class: int = 100):
    """
    Generate synthetic training data for demonstration.
    In production, use real hand tracking data.
    """
    print("Generating synthetic training data...")
    
    landmarks_list = []
    labels = []
    
    # Generate samples for each gesture class
    for class_idx in range(6):  # 6 gesture classes
        for _ in range(num_samples_per_class):
            # Generate random landmarks (21 points, 3D)
            landmarks = []
            for i in range(21):
                # Create patterns based on gesture class
                if class_idx == 0:  # move_cursor: open hand
                    x = np.random.uniform(0.3, 0.7)
                    y = np.random.uniform(0.3, 0.7)
                    z = np.random.uniform(-0.1, 0.1)
                elif class_idx == 1:  # left_click: index finger extended
                    x = np.random.uniform(0.4, 0.6)
                    y = np.random.uniform(0.4, 0.6)
                    z = np.random.uniform(-0.1, 0.1)
                    # Make index finger tip (8) more extended
                    if i == 8:
                        y -= 0.1
                elif class_idx == 2:  # right_click: middle finger extended
                    x = np.random.uniform(0.4, 0.6)
                    y = np.random.uniform(0.4, 0.6)
                    z = np.random.uniform(-0.1, 0.1)
                    if i == 12:
                        y -= 0.1
                elif class_idx == 3:  # scroll: all fingers extended
                    x = np.random.uniform(0.4, 0.6)
                    y = np.random.uniform(0.3, 0.5)
                    z = np.random.uniform(-0.1, 0.1)
                elif class_idx == 4:  # drag: pinch (thumb and index close)
                    x = np.random.uniform(0.4, 0.6)
                    y = np.random.uniform(0.4, 0.6)
                    z = np.random.uniform(-0.1, 0.1)
                    if i == 4:  # thumb tip
                        x += 0.02
                    if i == 8:  # index tip
                        x -= 0.02
                else:  # thumbs_up: thumb extended
                    x = np.random.uniform(0.4, 0.6)
                    y = np.random.uniform(0.4, 0.6)
                    z = np.random.uniform(-0.1, 0.1)
                    if i == 4:  # thumb tip
                        y -= 0.15
                
                # Create landmark-like object
                class Landmark:
                    def __init__(self, x, y, z):
                        self.x = x
                        self.y = y
                        self.z = z
                
                landmarks.append(Landmark(x, y, z))
            
            landmarks_list.append(landmarks)
            labels.append(class_idx)
    
    return landmarks_list, labels


def load_dataset_from_file(filepath: str):
    """Load dataset from pickle file."""
    if os.path.exists(filepath):
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        # Convert dicts back to Landmark objects
        landmarks_list = []
        for landmark_dicts in data['landmarks']:
            class Landmark:
                def __init__(self, x, y, z):
                    self.x = x
                    self.y = y
                    self.z = z
            landmarks = [Landmark(lm['x'], lm['y'], lm['z']) for lm in landmark_dicts]
            landmarks_list.append(landmarks)
        return landmarks_list, data['labels']
    return None, None


def save_dataset_to_file(landmarks_list, labels, filepath: str):
    """Save dataset to pickle file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    # Convert landmarks to list of dicts for pickle compatibility
    serializable_landmarks = []
    for landmarks in landmarks_list:
        landmark_dicts = [{'x': lm.x, 'y': lm.y, 'z': lm.z} for lm in landmarks]
        serializable_landmarks.append(landmark_dicts)
    with open(filepath, 'wb') as f:
        pickle.dump({'landmarks': serializable_landmarks, 'labels': labels}, f)
    print(f"Dataset saved to {filepath}")


def main():
    """Main training function."""
    print("=" * 50)
    print("Gesture CNN Model Training")
    print("=" * 50)
    
    # Check for existing dataset
    dataset_path = 'data/training_dataset.pkl'
    landmarks_list, labels = load_dataset_from_file(dataset_path)
    
    if landmarks_list is None:
        print("No existing dataset found. Generating synthetic data...")
        landmarks_list, labels = generate_synthetic_data(num_samples_per_class=200)
        save_dataset_to_file(landmarks_list, labels, dataset_path)
    else:
        print(f"Loaded dataset from {dataset_path}")
    
    # Create training data
    print("Preparing training data...")
    X, y = create_training_data_from_landmarks(landmarks_list, labels)
    
    print(f"Training data shape: {X.shape}")
    print(f"Labels shape: {y.shape}")
    
    # Split into train and validation
    split_idx = int(0.8 * len(X))
    X_train, X_val = X[:split_idx], X[split_idx:]
    y_train, y_val = y[:split_idx], y[split_idx:]
    
    print(f"Train samples: {len(X_train)}")
    print(f"Validation samples: {len(X_val)}")
    
    # Create and train model
    model_path = 'models/gesture_cnn.h5'
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    
    cnn = GestureCNN(model_path=model_path)
    
    print("\nStarting training...")
    history = cnn.train(
        X_train, y_train,
        X_val, y_val,
        epochs=100,
        batch_size=32
    )
    
    print("\nTraining complete!")
    print(f"Model saved to {model_path}")
    
    # Evaluate
    print("\nEvaluating on validation set...")
    loss, accuracy = cnn.model.evaluate(X_val, y_val, verbose=0)
    print(f"Validation Loss: {loss:.4f}")
    print(f"Validation Accuracy: {accuracy:.4f}")


if __name__ == '__main__':
    main()

