"""
Real-world gesture recognition testing framework.
Test actual gesture performance with visual feedback.
"""
import cv2
import numpy as np
from src.hand_tracking import HandTracker
from src.gesture_cnn import GestureCNN
import time
from collections import deque


class GestureTestbed:
    """Interactive testbed for evaluating gesture recognition in real-time."""
    
    GESTURE_CLASSES = [
        'move_cursor', 'left_click', 'right_click',
        'scroll', 'drag', 'thumbs_up'
    ]
    
    GESTURE_COLORS = {
        'move_cursor': (0, 255, 0),      # Green
        'left_click': (255, 0, 0),       # Blue
        'right_click': (0, 0, 255),      # Red
        'scroll': (255, 255, 0),         # Cyan
        'drag': (255, 0, 255),           # Magenta
        'thumbs_up': (0, 165, 255)       # Orange
    }
    
    def __init__(self, model_path='models/gesture_cnn.h5', camera_index=0, use_glove=False):
        """Initialize testbed."""
        mode = 'glove' if use_glove else 'hand'
        self.hand_tracker = HandTracker(mode=mode)
        self.gesture_model = GestureCNN(model_path=model_path)
        self.cap = cv2.VideoCapture(camera_index)
        
        # FPS tracking
        self.fps_deque = deque(maxlen=30)
        self.prev_time = time.time()
        
        # Gesture statistics
        self.gesture_counts = {g: 0 for g in self.GESTURE_CLASSES}
        self.confidence_scores = {g: [] for g in self.GESTURE_CLASSES}
        self.last_gesture = 'move_cursor'
        self.last_confidence = 0.0
        
        # Confidence threshold
        self.confidence_threshold = 0.6
    
    def run(self):
        """Run interactive testing session."""
        print("\n" + "="*60)
        print("GESTURE RECOGNITION TESTBED")
        print("="*60)
        print("Controls:")
        print("  's' - Save statistics")
        print("  'c' - Clear statistics")
        print("  'q' - Quit")
        print("="*60 + "\n")
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            
            # Detect hand
            detection_result, annotated_frame = self.hand_tracker.detect_hand(frame)
            
            # detection_result is landmarks (for hand) or centroid (for glove)
            landmarks = detection_result if self.hand_tracker.mode == 'hand' else None
            
            if landmarks:
                # Predict gesture
                gesture, confidence = self.gesture_model.predict(landmarks)
                
                if confidence >= self.confidence_threshold:
                    self.gesture_counts[gesture] += 1
                    self.confidence_scores[gesture].append(confidence)
                    self.last_gesture = gesture
                    self.last_confidence = confidence
                    
                    # Draw gesture info
                    self._draw_gesture_info(annotated_frame, gesture, confidence)
            
            # Draw FPS
            self._update_and_draw_fps(annotated_frame)
            
            # Display frame
            cv2.imshow('Gesture Testbed', annotated_frame)
            
            # Handle key press
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                self._save_statistics()
            elif key == ord('c'):
                self._clear_statistics()
        
        self.cap.release()
        cv2.destroyAllWindows()
    
    def _draw_landmarks(self, frame, landmarks):
        """Draw hand landmarks on frame."""
        h, w, _ = frame.shape
        
        for i, landmark in enumerate(landmarks):
            x = int(landmark.x * w)
            y = int(landmark.y * h)
            cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
            
            # Draw connections (finger bones)
            if i > 0 and i % 4 != 0:
                prev_landmark = landmarks[i-1]
                prev_x = int(prev_landmark.x * w)
                prev_y = int(prev_landmark.y * h)
                cv2.line(frame, (prev_x, prev_y), (x, y), (0, 255, 0), 2)
    
    def _draw_gesture_info(self, frame, gesture, confidence):
        """Draw current gesture and confidence on frame."""
        h, w, _ = frame.shape
        color = self.GESTURE_COLORS.get(gesture, (255, 255, 255))
        
        # Draw background rectangle
        text = f"{gesture}: {confidence:.2f}"
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1.2
        thickness = 2
        
        text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
        x_offset = 20
        y_offset = 100
        
        cv2.rectangle(frame, (x_offset - 5, y_offset - text_size[1] - 5),
                     (x_offset + text_size[0] + 5, y_offset + 5), color, -1)
        
        # Draw text
        cv2.putText(frame, text, (x_offset, y_offset),
                   font, font_scale, (255, 255, 255), thickness)
        
        # Draw confidence bar
        bar_width = 300
        bar_height = 30
        bar_x = x_offset
        bar_y = y_offset + 50
        
        # Background bar
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height),
                     (100, 100, 100), -1)
        
        # Confidence fill
        fill_width = int(bar_width * confidence)
        cv2.rectangle(frame, (bar_x, bar_y), (bar_x + fill_width, bar_y + bar_height),
                     color, -1)
        
        # Confidence text
        cv2.putText(frame, f"Confidence: {confidence*100:.1f}%",
                   (bar_x + 10, bar_y + 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    
    def _update_and_draw_fps(self, frame):
        """Calculate and display FPS."""
        current_time = time.time()
        time_diff = current_time - self.prev_time
        if time_diff > 0:
            fps = 1 / time_diff
        else:
            fps = 0.0
        self.fps_deque.append(fps)
        self.prev_time = current_time
        
        avg_fps = np.mean(self.fps_deque)
        
        cv2.putText(frame, f"FPS: {avg_fps:.1f}", (20, 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    def _save_statistics(self):
        """Save statistics to file."""
        stats_file = 'results/testbed_statistics.txt'
        
        with open(stats_file, 'w') as f:
            f.write("="*60 + "\n")
            f.write("GESTURE RECOGNITION TESTBED STATISTICS\n")
            f.write("="*60 + "\n\n")
            
            total_recognitions = sum(self.gesture_counts.values())
            f.write(f"Total Recognitions: {total_recognitions}\n\n")
            
            f.write("Gesture Distribution:\n")
            f.write("-"*60 + "\n")
            for gesture in self.GESTURE_CLASSES:
                count = self.gesture_counts[gesture]
                percent = (count / total_recognitions * 100) if total_recognitions > 0 else 0
                f.write(f"  {gesture:15}: {count:4} ({percent:5.1f}%)\n")
            
            f.write("\nAverage Confidence per Gesture:\n")
            f.write("-"*60 + "\n")
            for gesture in self.GESTURE_CLASSES:
                if self.confidence_scores[gesture]:
                    avg_conf = np.mean(self.confidence_scores[gesture])
                    min_conf = np.min(self.confidence_scores[gesture])
                    max_conf = np.max(self.confidence_scores[gesture])
                    f.write(f"  {gesture:15}: Avg={avg_conf:.3f}, "
                           f"Min={min_conf:.3f}, Max={max_conf:.3f}\n")
                else:
                    f.write(f"  {gesture:15}: No data\n")
        
        print(f"Statistics saved to {stats_file}")
    
    def _clear_statistics(self):
        """Clear statistics."""
        self.gesture_counts = {g: 0 for g in self.GESTURE_CLASSES}
        self.confidence_scores = {g: [] for g in self.GESTURE_CLASSES}
        print("Statistics cleared.")


def main():
    """Run testbed."""
    testbed = GestureTestbed(
        model_path='models/gesture_cnn.h5',
        camera_index=0,
        use_glove=False  # Set to True for glove-based tracking
    )
    
    testbed.run()


if __name__ == '__main__':
    main()
