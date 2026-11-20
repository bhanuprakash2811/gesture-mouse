"""
CNN model for gesture classification.
Supports training and inference.
"""
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import os
from typing import List, Tuple, Optional
from src.utils import extract_landmark_features, calculate_distances, calculate_angles


class GestureCNN:
    """CNN model for classifying hand gestures."""
    
    GESTURE_CLASSES = [
        'move_cursor',
        'left_click',
        'right_click',
        'scroll',
        'drag',
        'thumbs_up'  # Exit gesture
    ]
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize CNN model.
        
        Args:
            model_path: Path to saved model (.h5 file). If None, creates new model.
        """
        self.model = None
        self.model_path = model_path or 'models/gesture_cnn.h5'
        
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
        else:
            self.build_model()
    
    def build_model(self):
        """Build CNN architecture for gesture classification."""
        # Input: 63 features (21 landmarks * 3 coordinates)
        input_shape = (63,)
        
        self.model = keras.Sequential([
            layers.Dense(128, activation='relu', input_shape=input_shape),
            layers.Dropout(0.3),
            layers.Dense(64, activation='relu'),
            layers.Dropout(0.3),
            layers.Dense(32, activation='relu'),
            layers.Dropout(0.2),
            layers.Dense(len(self.GESTURE_CLASSES), activation='softmax')
        ])
        
        self.model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
    
    def load_model(self, model_path: str):
        """Load pre-trained model."""
        try:
            self.model = keras.models.load_model(model_path)
            print(f"Model loaded from {model_path}")
        except Exception as e:
            print(f"Error loading model: {e}. Creating new model.")
            self.build_model()
    
    def save_model(self, model_path: Optional[str] = None):
        """Save model to file."""
        path = model_path or self.model_path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.model.save(path)
        print(f"Model saved to {path}")
    
    def predict(self, landmarks: List) -> Tuple[str, float]:
        """
        Predict gesture from landmarks.
        
        Returns:
            (gesture_class, confidence)
        """
        if landmarks is None or len(landmarks) == 0:
            return 'move_cursor', 0.0
        
        # Extract features
        features = extract_landmark_features(landmarks)
        features = features.reshape(1, -1)
        
        # Predict
        predictions = self.model.predict(features, verbose=0)
        class_idx = np.argmax(predictions[0])
        confidence = float(predictions[0][class_idx])
        
        return self.GESTURE_CLASSES[class_idx], confidence
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray,
              X_val: np.ndarray = None, y_val: np.ndarray = None,
              epochs: int = 50, batch_size: int = 32):
        """
        Train the CNN model.
        
        Args:
            X_train: Training features (N, 63)
            y_train: Training labels (N, num_classes) - one-hot encoded
            X_val: Validation features
            y_val: Validation labels
            epochs: Number of training epochs
            batch_size: Batch size
        """
        callbacks = [
            keras.callbacks.EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True),
            keras.callbacks.ModelCheckpoint(self.model_path, save_best_only=True, monitor='val_loss')
        ]
        
        validation_data = None
        if X_val is not None and y_val is not None:
            validation_data = (X_val, y_val)
        
        history = self.model.fit(
            X_train, y_train,
            validation_data=validation_data,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=1
        )
        
        self.save_model()
        return history


def create_training_data_from_landmarks(landmarks_list: List[List], 
                                       labels: List[int]) -> Tuple[np.ndarray, np.ndarray]:
    """
    Create training data from landmark sequences.
    
    Args:
        landmarks_list: List of landmark sequences
        labels: List of class labels (0-5)
    
    Returns:
        (X, y) where X is features and y is one-hot encoded labels
    """
    X = []
    y = []
    
    for landmarks, label in zip(landmarks_list, labels):
        features = extract_landmark_features(landmarks)
        X.append(features)
        y.append(label)
    
    X = np.array(X)
    y = keras.utils.to_categorical(y, num_classes=len(GestureCNN.GESTURE_CLASSES))
    
    return X, y

