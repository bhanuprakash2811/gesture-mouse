"""
Enhanced training script that loads CSV data and generates evaluation metrics.
"""
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
from sklearn.preprocessing import LabelEncoder
from src.gesture_cnn import GestureCNN
from src.utils import extract_landmark_features
import os
import json
from datetime import datetime


def load_csv_data(filepath: str):
    """Load gesture landmarks from CSV file."""
    print(f"Loading data from {filepath}...")
    df = pd.read_csv(filepath)
    
    print(f"Dataset shape: {df.shape}")
    print(f"Gesture labels: {df['gesture_label'].unique()}")
    print(f"Label distribution:\n{df['gesture_label'].value_counts()}\n")
    
    return df


def create_landmarks_from_csv(df):
    """Convert CSV data to landmark objects for training."""
    landmarks_list = []
    labels = []
    
    # Get gesture label mapping
    unique_labels = df['gesture_label'].unique()
    label_to_idx = {label: idx for idx, label in enumerate(unique_labels)}
    idx_to_label = {idx: label for label, idx in label_to_idx.items()}
    
    landmark_cols = [col for col in df.columns if col != 'gesture_label']
    
    for idx, row in df.iterrows():
        # Create landmark-like objects
        landmarks = []
        for i in range(21):  # 21 hand landmarks
            x_key = f'landmark_{i}_x'
            y_key = f'landmark_{i}_y'
            z_key = f'landmark_{i}_z'
            
            class Landmark:
                def __init__(self, x, y, z):
                    self.x = float(x)
                    self.y = float(y)
                    self.z = float(z)
            
            landmark = Landmark(row[x_key], row[y_key], row[z_key])
            landmarks.append(landmark)
        
        landmarks_list.append(landmarks)
        labels.append(label_to_idx[row['gesture_label']])
    
    return landmarks_list, labels, label_to_idx, idx_to_label


def prepare_training_data(landmarks_list, labels):
    """Prepare features and one-hot encoded labels."""
    X = []
    y = []
    
    for landmarks, label in zip(landmarks_list, labels):
        features = extract_landmark_features(landmarks)
        X.append(features)
        y.append(label)
    
    X = np.array(X)
    num_classes = len(set(labels))
    y_encoded = keras.utils.to_categorical(y, num_classes=num_classes)
    
    return X, y_encoded, y


def train_and_evaluate():
    """Main training and evaluation function."""
    print("\n" + "=" * 70)
    print("GESTURE CNN MODEL - TRAINING AND EVALUATION")
    print("=" * 70 + "\n")
    
    # Load CSV data
    csv_path = 'data/gesture_landmarks.csv'
    df = load_csv_data(csv_path)
    
    # Create landmarks from CSV
    landmarks_list, labels, label_to_idx, idx_to_label = create_landmarks_from_csv(df)
    
    print(f"Created {len(landmarks_list)} training samples")
    print(f"Gesture classes: {list(label_to_idx.keys())}\n")
    
    # Prepare training data
    X, y_encoded, y_labels = prepare_training_data(landmarks_list, labels)
    
    print(f"Feature matrix shape: {X.shape}")
    print(f"Encoded labels shape: {y_encoded.shape}\n")
    
    # Split into train, validation, and test sets
    print("Splitting data...")
    X_temp, X_test, y_temp, y_test = train_test_split(
        X, y_encoded, test_size=0.15, random_state=42, stratify=y_labels
    )
    
    y_temp_labels = np.argmax(y_temp, axis=1)
    X_train, X_val, y_train, y_val = train_test_split(
        X_temp, y_temp, test_size=0.15, random_state=42, stratify=y_temp_labels
    )
    
    print(f"Train samples: {len(X_train)}")
    print(f"Validation samples: {len(X_val)}")
    print(f"Test samples: {len(X_test)}\n")
    
    # Create and train model
    model_path = 'models/gesture_cnn.h5'
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    
    print("Building and training model...")
    cnn = GestureCNN(model_path=None)  # Create new model
    
    history = cnn.train(
        X_train, y_train,
        X_val, y_val,
        epochs=100,
        batch_size=32
    )
    
    # Save model
    cnn.save_model(model_path)
    
    # Evaluate on test set
    print("\n" + "=" * 70)
    print("EVALUATION RESULTS")
    print("=" * 70 + "\n")
    
    # Get predictions
    y_test_pred_probs = cnn.model.predict(X_test, verbose=0)
    y_test_pred = np.argmax(y_test_pred_probs, axis=1)
    y_test_true = np.argmax(y_test, axis=1)
    
    # Calculate metrics
    accuracy = accuracy_score(y_test_true, y_test_pred)
    precision_weighted = precision_score(y_test_true, y_test_pred, average='weighted', zero_division=0)
    recall_weighted = recall_score(y_test_true, y_test_pred, average='weighted', zero_division=0)
    f1_weighted = f1_score(y_test_true, y_test_pred, average='weighted', zero_division=0)
    
    print(f"Overall Accuracy: {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"Weighted Precision: {precision_weighted:.4f}")
    print(f"Weighted Recall: {recall_weighted:.4f}")
    print(f"Weighted F1-Score: {f1_weighted:.4f}\n")
    
    # Detailed classification report
    print("DETAILED CLASSIFICATION REPORT")
    print("-" * 70)
    gesture_names = [idx_to_label[i] for i in range(len(label_to_idx))]
    class_report = classification_report(
        y_test_true, y_test_pred,
        target_names=gesture_names,
        digits=4,
        zero_division=0
    )
    print(class_report)
    
    # Confusion matrix
    print("\nCONFUSION MATRIX")
    print("-" * 70)
    conf_matrix = confusion_matrix(y_test_true, y_test_pred)
    print("Rows = True labels, Columns = Predicted labels")
    print(f"{'Gesture':<20}", end='')
    for name in gesture_names:
        print(f"{name:<15}", end='')
    print()
    for i, name in enumerate(gesture_names):
        print(f"{name:<20}", end='')
        for j in range(len(gesture_names)):
            print(f"{conf_matrix[i, j]:<15}", end='')
        print()
    
    print("\n" + "=" * 70)
    print("VALIDATION AND TRAINING SET METRICS")
    print("=" * 70 + "\n")
    
    # Validation metrics
    y_val_pred_probs = cnn.model.predict(X_val, verbose=0)
    y_val_pred = np.argmax(y_val_pred_probs, axis=1)
    y_val_true = np.argmax(y_val, axis=1)
    
    val_accuracy = accuracy_score(y_val_true, y_val_pred)
    val_precision = precision_score(y_val_true, y_val_pred, average='weighted', zero_division=0)
    val_recall = recall_score(y_val_true, y_val_pred, average='weighted', zero_division=0)
    
    print(f"Validation Accuracy: {val_accuracy:.4f} ({val_accuracy*100:.2f}%)")
    print(f"Validation Precision: {val_precision:.4f}")
    print(f"Validation Recall: {val_recall:.4f}\n")
    
    # Training metrics
    y_train_pred_probs = cnn.model.predict(X_train, verbose=0)
    y_train_pred = np.argmax(y_train_pred_probs, axis=1)
    y_train_true = np.argmax(y_train, axis=1)
    
    train_accuracy = accuracy_score(y_train_true, y_train_pred)
    train_precision = precision_score(y_train_true, y_train_pred, average='weighted', zero_division=0)
    train_recall = recall_score(y_train_true, y_train_pred, average='weighted', zero_division=0)
    
    print(f"Training Accuracy: {train_accuracy:.4f} ({train_accuracy*100:.2f}%)")
    print(f"Training Precision: {train_precision:.4f}")
    print(f"Training Recall: {train_recall:.4f}\n")
    
    # Save results to file
    results = {
        'timestamp': datetime.now().isoformat(),
        'dataset': {
            'total_samples': len(X),
            'train_samples': len(X_train),
            'val_samples': len(X_val),
            'test_samples': len(X_test),
            'gesture_classes': gesture_names
        },
        'test_metrics': {
            'accuracy': float(accuracy),
            'precision_weighted': float(precision_weighted),
            'recall_weighted': float(recall_weighted),
            'f1_weighted': float(f1_weighted)
        },
        'validation_metrics': {
            'accuracy': float(val_accuracy),
            'precision': float(val_precision),
            'recall': float(val_recall)
        },
        'training_metrics': {
            'accuracy': float(train_accuracy),
            'precision': float(train_precision),
            'recall': float(train_recall)
        },
        'confusion_matrix': conf_matrix.tolist(),
        'per_class_metrics': {}
    }
    
    # Add per-class metrics
    for i, name in enumerate(gesture_names):
        tp = conf_matrix[i, i]
        fp = conf_matrix[:, i].sum() - tp
        fn = conf_matrix[i, :].sum() - tp
        tn = conf_matrix.sum() - tp - fp - fn
        
        precision_class = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall_class = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1_class = 2 * (precision_class * recall_class) / (precision_class + recall_class) if (precision_class + recall_class) > 0 else 0
        
        results['per_class_metrics'][name] = {
            'precision': float(precision_class),
            'recall': float(recall_class),
            'f1_score': float(f1_class),
            'support': int(conf_matrix[i, :].sum())
        }
    
    # Save results
    results_file = 'results/evaluation_results.json'
    os.makedirs(os.path.dirname(results_file), exist_ok=True)
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {results_file}")
    
    print("\n" + "=" * 70)
    print("TRAINING COMPLETE!")
    print("=" * 70 + "\n")
    
    return results


if __name__ == '__main__':
    results = train_and_evaluate()
