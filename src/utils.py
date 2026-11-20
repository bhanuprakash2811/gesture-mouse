"""
Utility functions for feature extraction and preprocessing.
"""
import numpy as np
from typing import List, Tuple, Optional
import cv2

# Try to import C++ optimization module (optional)
try:
    import fast_math
    HAS_FAST_MATH = True
except ImportError:
    HAS_FAST_MATH = False
    print("Warning: C++ fast_math module not found. Using Python fallback.")


def extract_landmark_features(landmarks: List) -> np.ndarray:
    """
    Extract features from MediaPipe landmarks (21 points, 3D coordinates).
    Returns flattened array of 63 features (21 * 3).
    """
    if not landmarks or len(landmarks) == 0:
        return np.zeros(63, dtype=np.float32)
    
    features = []
    for landmark in landmarks:
        features.extend([landmark.x, landmark.y, landmark.z])
    
    # Pad if necessary
    while len(features) < 63:
        features.append(0.0)
    
    return np.array(features[:63], dtype=np.float32)


def calculate_distances(landmarks: List) -> np.ndarray:
    """
    Calculate distances between key landmark points.
    Returns array of distances for gesture classification.
    Uses C++ module if available for better performance.
    """
    if not landmarks or len(landmarks) < 2:
        return np.zeros(10, dtype=np.float32)
    
    # Try to use C++ module if available
    if HAS_FAST_MATH:
        try:
            # Convert landmarks to flat array
            flat_landmarks = []
            for landmark in landmarks:
                flat_landmarks.extend([landmark.x, landmark.y, landmark.z])
            # Pad to 63 (21 landmarks * 3)
            while len(flat_landmarks) < 63:
                flat_landmarks.append(0.0)
            
            distances = fast_math.compute_distances(flat_landmarks[:63])
            # Return first 10 distances
            return np.array(distances[:10], dtype=np.float32)
        except Exception as e:
            print(f"Error using C++ module: {e}. Falling back to Python.")
    
    # Python fallback
    key_indices = [0, 4, 8, 12, 16, 20]
    distances = []
    
    for i in range(len(key_indices)):
        for j in range(i + 1, len(key_indices)):
            if key_indices[i] < len(landmarks) and key_indices[j] < len(landmarks):
                p1 = landmarks[key_indices[i]]
                p2 = landmarks[key_indices[j]]
                dist = np.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2 + (p1.z - p2.z)**2)
                distances.append(dist)
    
    # Pad to fixed size
    while len(distances) < 10:
        distances.append(0.0)
    
    return np.array(distances[:10], dtype=np.float32)


def calculate_angles(landmarks: List) -> np.ndarray:
    """
    Calculate angles between key landmark points.
    """
    if not landmarks or len(landmarks) < 3:
        return np.zeros(5, dtype=np.float32)
    
    angles = []
    # Angle between thumb-index-middle
    if len(landmarks) > 12:
        p1 = landmarks[4]  # thumb tip
        p2 = landmarks[8]  # index tip
        p3 = landmarks[12]  # middle tip
        
        v1 = np.array([p1.x - p2.x, p1.y - p2.y])
        v2 = np.array([p3.x - p2.x, p3.y - p2.y])
        
        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
        angle = np.arccos(np.clip(cos_angle, -1.0, 1.0))
        angles.append(angle)
    
    # Add more angle calculations as needed
    while len(angles) < 5:
        angles.append(0.0)
    
    return np.array(angles[:5], dtype=np.float32)


def normalize_landmarks(landmarks: List, image_width: int, image_height: int) -> List:
    """
    Normalize landmarks to image coordinates.
    """
    normalized = []
    for landmark in landmarks:
        normalized.append({
            'x': landmark.x * image_width,
            'y': landmark.y * image_height,
            'z': landmark.z
        })
    return normalized


def exponential_moving_average(current: Tuple[float, float], 
                               previous: Tuple[float, float], 
                               alpha: float = 0.7) -> Tuple[float, float]:
    """
    Apply exponential moving average for smooth cursor movement.
    """
    if previous is None:
        return current
    
    x = alpha * current[0] + (1 - alpha) * previous[0]
    y = alpha * current[1] + (1 - alpha) * previous[1]
    return (x, y)


def get_glove_mask(frame: np.ndarray, hsv_lower: Tuple[int, int, int], 
                   hsv_upper: Tuple[int, int, int]) -> np.ndarray:
    """
    Create mask for colored glove detection.
    Default: red glove (can be changed to blue or other colors).
    """
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, hsv_lower, hsv_upper)
    
    # Morphological operations to clean up mask
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    
    return mask


def get_glove_centroid(mask: np.ndarray) -> Optional[Tuple[int, int]]:
    """
    Calculate centroid of glove mask.
    """
    moments = cv2.moments(mask)
    if moments["m00"] != 0:
        cx = int(moments["m10"] / moments["m00"])
        cy = int(moments["m01"] / moments["m00"])
        return (cx, cy)
    return None


def get_screen_resolution() -> Tuple[int, int]:
    """
    Get screen resolution for cursor mapping.
    """
    try:
        import pyautogui
        return pyautogui.size()
    except:
        return (1920, 1080)  # Default

