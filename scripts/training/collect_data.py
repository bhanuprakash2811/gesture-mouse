"""
Data collection script for training the gesture CNN.
Records hand landmarks for each gesture class.
"""
import cv2
import mediapipe as mp
import numpy as np
import pickle
import os
from src.hand_tracking import HandTracker
from src.gesture_cnn import GestureCNN


def collect_gesture_data():
    """Interactive data collection for gesture training."""
    print("=" * 50)
    print("Gesture Data Collection Tool")
    print("=" * 50)
    
    gesture_classes = GestureCNN.GESTURE_CLASSES
    print("\nGesture Classes:")
    for i, cls in enumerate(gesture_classes):
        print(f"  {i}: {cls}")
    
    print("\nInstructions:")
    print("1. Press number key (0-5) to select gesture class")
    print("2. Show the gesture to camera")
    print("3. Press SPACE to record sample")
    print("4. Press 's' to save dataset")
    print("5. Press 'q' to quit")
    
    # Initialize
    tracker = HandTracker(mode='hand')
    if not tracker.initialize_camera():
        print("Error: Could not initialize camera")
        return
    
    # Storage
    all_landmarks = []
    all_labels = []
    current_class = 0
    sample_count = 0
    
    print(f"\nCurrent class: {gesture_classes[current_class]} (Press 0-5 to change)")
    
    try:
        while True:
            frame = tracker.get_frame()
            if frame is None:
                break
            
            landmarks, annotated_frame = tracker.detect_hand(frame)
            
            # Display current class and sample count
            cv2.putText(annotated_frame, f"Class: {gesture_classes[current_class]}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(annotated_frame, f"Samples: {sample_count}", 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(annotated_frame, "SPACE: Record | 0-5: Change class | s: Save | q: Quit", 
                       (10, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            if landmarks:
                cv2.putText(annotated_frame, "Hand detected - Press SPACE to record", 
                           (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            else:
                cv2.putText(annotated_frame, "No hand detected", 
                           (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
            cv2.imshow('Data Collection', annotated_frame)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q'):
                break
            elif key == ord('s'):
                # Save dataset
                dataset_path = 'data/collected_dataset.pkl'
                os.makedirs(os.path.dirname(dataset_path), exist_ok=True)
                
                # Convert landmarks to dicts for pickling
                serializable_landmarks = []
                for sample_landmarks in all_landmarks:
                    landmark_dicts = [{'x': lm.x, 'y': lm.y, 'z': lm.z} for lm in sample_landmarks]
                    serializable_landmarks.append(landmark_dicts)
                    
                with open(dataset_path, 'wb') as f:
                    pickle.dump({'landmarks': serializable_landmarks, 'labels': all_labels}, f)
                print(f"\nDataset saved: {len(all_landmarks)} samples")
            elif key == ord(' '):  # Space bar
                if landmarks:
                    all_landmarks.append(landmarks)
                    all_labels.append(current_class)
                    sample_count += 1
                    print(f"Recorded sample {sample_count} for class {gesture_classes[current_class]}")
            elif ord('0') <= key <= ord('5'):
                current_class = key - ord('0')
                sample_count = sum(1 for label in all_labels if label == current_class)
                print(f"Switched to class: {gesture_classes[current_class]} (existing samples: {sample_count})")
    
    except KeyboardInterrupt:
        print("\nInterrupted")
    
    finally:
        tracker.release()
        cv2.destroyAllWindows()
        
        # Save on exit
        if all_landmarks:
            dataset_path = 'data/collected_dataset.pkl'
            os.makedirs(os.path.dirname(dataset_path), exist_ok=True)
            
            serializable_landmarks = []
            for sample_landmarks in all_landmarks:
                landmark_dicts = [{'x': lm.x, 'y': lm.y, 'z': lm.z} for lm in sample_landmarks]
                serializable_landmarks.append(landmark_dicts)
                
            with open(dataset_path, 'wb') as f:
                pickle.dump({'landmarks': serializable_landmarks, 'labels': all_labels}, f)
            print(f"\nFinal dataset saved: {len(all_landmarks)} samples")


if __name__ == '__main__':
    collect_gesture_data()

