"""
Hand tracking module using MediaPipe (bare-hand) and OpenCV (glove mode).
"""
import cv2
import mediapipe as mp
import numpy as np
from typing import List, Optional, Tuple
from src.utils import get_glove_mask, get_glove_centroid, normalize_landmarks


class HandTracker:
    """Hand tracking class supporting both bare-hand and glove modes."""
    
    def __init__(self, mode: str = 'hand'):
        """
        Initialize hand tracker.
        
        Args:
            mode: 'hand' for MediaPipe bare-hand tracking, 'glove' for colored glove tracking
        """
        self.mode = mode
        self.mp_hands = None
        self.hands = None
        self.cap = None
        
        if mode == 'hand':
            # Initialize MediaPipe
            self.mp_hands = mp.solutions.hands
            self.hands = self.mp_hands.Hands(
                static_image_mode=False,
                max_num_hands=1,
                min_detection_confidence=0.7,
                min_tracking_confidence=0.5
            )
            self.mp_draw = mp.solutions.drawing_utils
        
        # Glove mode parameters (default: red glove)
        self.hsv_lower = np.array([0, 50, 50])  # Red lower bound
        self.hsv_upper = np.array([10, 255, 255])  # Red upper bound
        
        # For blue glove, use:
        # self.hsv_lower = np.array([100, 50, 50])
        # self.hsv_upper = np.array([130, 255, 255])
    
    def initialize_camera(self, camera_index: int = 0) -> bool:
        """Initialize camera capture."""
        try:
            self.cap = cv2.VideoCapture(camera_index)
            if not self.cap.isOpened():
                return False
            # Set resolution (lower default to improve FPS)
            # Use 320x240 for faster processing; increase if you need higher visual fidelity
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
            return True
        except Exception as e:
            print(f"Error initializing camera: {e}")
            return False
    
    def detect_hand(self, frame: np.ndarray) -> Tuple[Optional[List], Optional[np.ndarray]]:
        """
        Detect hand in frame.
        
        Returns:
            (landmarks, annotated_frame) for hand mode
            (centroid, mask) for glove mode
        """
        if self.mode == 'hand':
            return self._detect_bare_hand(frame)
        else:
            return self._detect_glove(frame)
    
    def _detect_bare_hand(self, frame: np.ndarray) -> Tuple[Optional[List], Optional[np.ndarray]]:
        """Detect bare hand using MediaPipe."""
        if self.hands is None:
            return None, frame
        
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        landmarks = None
        annotated_frame = frame.copy()
        
        if results.multi_hand_landmarks:
            # Get first hand
            hand_landmarks = results.multi_hand_landmarks[0]
            landmarks = hand_landmarks.landmark
            
            # Draw landmarks
            self.mp_draw.draw_landmarks(
                annotated_frame,
                hand_landmarks,
                self.mp_hands.HAND_CONNECTIONS,
                self.mp_draw.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                self.mp_draw.DrawingSpec(color=(255, 0, 0), thickness=2)
            )
        
        return landmarks, annotated_frame
    
    def _detect_glove(self, frame: np.ndarray) -> Tuple[Optional[Tuple[int, int]], Optional[np.ndarray]]:
        """Detect colored glove using OpenCV."""
        mask = get_glove_mask(frame, self.hsv_lower, self.hsv_upper)
        centroid = get_glove_centroid(mask)
        
        annotated_frame = frame.copy()
        if centroid:
            cv2.circle(annotated_frame, centroid, 10, (0, 255, 0), -1)
            cv2.circle(annotated_frame, centroid, 20, (0, 255, 0), 2)
        
        return centroid, annotated_frame
    
    def get_frame(self) -> Optional[np.ndarray]:
        """Get next frame from camera."""
        if self.cap is None:
            return None
        
        ret, frame = self.cap.read()
        if ret:
            return frame
        return None
    
    def release(self):
        """Release camera resources."""
        if self.cap is not None:
            self.cap.release()
        cv2.destroyAllWindows()
    
    def set_glove_color(self, color: str = 'red'):
        """
        Set glove color for detection.
        
        Args:
            color: 'red' or 'blue'
        """
        if color.lower() == 'red':
            self.hsv_lower = np.array([0, 50, 50])
            self.hsv_upper = np.array([10, 255, 255])
        elif color.lower() == 'blue':
            self.hsv_lower = np.array([100, 50, 50])
            self.hsv_upper = np.array([130, 255, 255])
        else:
            print(f"Unknown color: {color}. Using red as default.")

