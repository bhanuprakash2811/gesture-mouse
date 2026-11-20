"""
Main entry point for Gesture Controlled Virtual Mouse.
Supports both bare-hand and glove modes with voice commands.
"""
import argparse
import cv2
import sys
import os
import time

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.hand_tracking import HandTracker
from src.gesture_cnn import GestureCNN
from src.voice_commands import VoiceCommandProcessor
from src.mouse_controller import MouseController
from src.utils import extract_landmark_features
from typing import Optional, Tuple


class GestureMouseSystem:
    """Main system class integrating all components."""
    
    def __init__(self, mode: str = 'hand', model_path: str = 'models/gesture_cnn.h5', target_fps: int = 30):
        """
        Initialize gesture mouse system.
        
        Args:
            mode: 'hand' for bare-hand tracking, 'glove' for colored glove
            model_path: Path to trained CNN model
        """
        self.mode = mode
        self.hand_tracker = HandTracker(mode=mode)
        self.gesture_cnn = GestureCNN(model_path=model_path)
        # Balanced smoothing: more aggressive to eliminate jitter
        self.mouse_controller = MouseController(
            smoothing_alpha=0.5,  # Lower alpha -> more smoothing (reduces jitter)
            window_size=5,        # Larger window to smooth out noisy detections
            interpolation_steps=0,  # No interpolation to avoid added latency
            max_jump_distance=300.0  # Filter out jumps larger than 300 pixels (loosened to prevent edge lock)
        )
        self.voice_processor = VoiceCommandProcessor(callback=self._on_voice_command)
        # Target processing FPS (detection/classification)
        self.target_fps = max(1, int(target_fps))
        # Voice scroll tuning
        self.voice_scroll_amount = 5
        self.voice_scroll_fast_amount = 20
        self.voice_scroll_slow_amount = 2
        
        self.running = False
        self.last_gesture = None
        self.last_gesture_time = 0
        self.gesture_cooldown = 0.3  # Reduced cooldown for better responsiveness
        
        # For drag detection
        self.drag_active = False
        self.pinch_threshold = 0.05  # Distance threshold for pinch detection
        # For scroll tracking
        self.last_scroll_pos = None
        self.scroll_sensitivity = 800  # multiplier to convert normalized delta to scroll units
        
        # For exit gesture (thumbs_up) - require holding for 3 seconds (increased for safety)
        self.thumbs_up_start_time = None
        self.thumbs_up_hold_duration = 3.0  # Must hold thumbs up for 3 seconds
        self.thumbs_up_required_count = 10  # Must detect thumbs_up in 10 consecutive frames
        self.thumbs_up_detection_count = 0
    
    def initialize(self) -> bool:
        """Initialize all components."""
        print("Initializing Gesture Controlled Virtual Mouse...")
        
        # Initialize camera
        if not self.hand_tracker.initialize_camera():
            print("Error: Could not initialize camera")
            return False
        
        # Initialize voice processor
        try:
            self.voice_processor.start_listening()
            print("Voice commands enabled")
        except Exception as e:
            print(f"Warning: Voice commands not available: {e}")
        
        print(f"System initialized in {self.mode} mode")
        return True
    
    def _on_voice_command(self, command: str):
        """Callback for voice commands."""
        print(f"Voice command received: {command}")
        # Handle voice commands directly (mapping names produced by VoiceCommandProcessor)
        if command == 'left_click':
            self.mouse_controller.left_click()
        elif command == 'right_click':
            self.mouse_controller.right_click()
        elif command == 'scroll_up':
            self.mouse_controller.scroll('up', self.voice_scroll_amount)
        elif command == 'scroll_down':
            self.mouse_controller.scroll('down', self.voice_scroll_amount)
        elif command == 'scroll_up_fast':
            self.mouse_controller.scroll('up', self.voice_scroll_fast_amount)
        elif command == 'scroll_down_fast':
            self.mouse_controller.scroll('down', self.voice_scroll_fast_amount)
        elif command == 'scroll_up_slow':
            self.mouse_controller.scroll('up', self.voice_scroll_slow_amount)
        elif command == 'scroll_down_slow':
            self.mouse_controller.scroll('down', self.voice_scroll_slow_amount)
        elif command == 'screenshot':
            self.mouse_controller.screenshot()
        elif command == 'exit':
            self.running = False
    
    def _detect_pinch(self, landmarks) -> bool:
        """Detect pinch gesture (thumb and index finger close together)."""
        if landmarks is None or len(landmarks) < 9:
            return False
        
        # Thumb tip (4) and index tip (8)
        thumb = landmarks[4]
        index = landmarks[8]
        
        distance = ((thumb.x - index.x)**2 + (thumb.y - index.y)**2)**0.5
        return distance < self.pinch_threshold
    
    def _detect_gesture_rules(self, landmarks) -> Optional[Tuple[str, float]]:
        """
        Rule-based gesture detection as fallback/complement to CNN.
        Returns (gesture, confidence) or None if no clear gesture.
        """
        if landmarks is None or len(landmarks) < 21:
            return None
        
        # MediaPipe landmark indices
        # Thumb: 4 (tip), 3 (IP), 2 (MCP)
        # Index: 8 (tip), 6 (PIP), 5 (MCP)
        # Middle: 12 (tip), 10 (PIP), 9 (MCP)
        # Ring: 16 (tip), 14 (PIP), 13 (MCP)
        # Pinky: 20 (tip), 18 (PIP), 17 (MCP)
        
        # Helper function to check if finger is extended
        def is_finger_extended(tip, pip, mcp):
            """Check if finger is extended (tip is above PIP joint)."""
            return tip.y < pip.y
        
        # Check each finger
        thumb_extended_x = landmarks[4].x > landmarks[3].x  # Thumb extends sideways (for left hand)
        thumb_extended_y = landmarks[4].y < landmarks[3].y  # Thumb extends upward (thumbs up)
        index_extended = is_finger_extended(landmarks[8], landmarks[6], landmarks[5])
        middle_extended = is_finger_extended(landmarks[12], landmarks[10], landmarks[9])
        ring_extended = is_finger_extended(landmarks[16], landmarks[14], landmarks[13])
        pinky_extended = is_finger_extended(landmarks[20], landmarks[18], landmarks[17])
        
        # Count extended fingers (excluding thumb)
        extended_count = sum([index_extended, middle_extended, ring_extended, pinky_extended])
        
        # Detect pinch (thumb and index close)
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        pinch_distance = ((thumb_tip.x - index_tip.x)**2 + (thumb_tip.y - index_tip.y)**2)**0.5
        
        # Rule-based gesture detection (order matters - check specific gestures first)
        if pinch_distance < 0.05:  # Pinch detected
            return ('drag', 0.9)
        elif index_extended and middle_extended and ring_extended and not pinky_extended:
            return ('middle_click', 0.85)  # Index + Middle + Ring (3 fingers)
        elif index_extended and middle_extended and not ring_extended and not pinky_extended:
            return ('double_click', 0.85)  # Index + Middle (Peace sign)
        elif pinky_extended and not index_extended and not middle_extended and not ring_extended:
            return ('screenshot', 0.85)  # Only Pinky
        elif index_extended and not middle_extended and not ring_extended and not pinky_extended:
            return ('left_click', 0.85)  # Only index finger
        elif middle_extended and not index_extended and not ring_extended and not pinky_extended:
            return ('right_click', 0.85)  # Only middle finger
        elif extended_count >= 4:  # All 4 fingers extended
            return ('scroll', 0.8)
        elif extended_count <= 1:  # Mostly closed hand
            return ('move_cursor', 0.7)  # Default to cursor movement
        
        return None  # No clear gesture
    
    def _get_hand_position(self, landmarks, frame_width: int, frame_height: int) -> Optional[Tuple[float, float]]:
        """Get hand position for cursor movement."""
        if landmarks is None or len(landmarks) == 0:
            return None
        
        # Use index finger tip (landmark 8) or middle finger tip (landmark 12)
        if len(landmarks) > 12:
            # Use middle finger tip for more stable cursor
            pos = landmarks[12]
            return (pos.x, pos.y)
        elif len(landmarks) > 8:
            pos = landmarks[8]
            return (pos.x, pos.y)
        
        return None
    
    def _get_glove_position(self, centroid, frame_width: int, frame_height: int) -> Optional[Tuple[float, float]]:
        """Get glove position for cursor movement."""
        if centroid is None:
            return None
        
        # Normalize to 0-1
        x = centroid[0] / frame_width
        y = centroid[1] / frame_height
        return (x, y)
    
    def _classify_gesture(self, landmarks) -> Tuple[str, float]:
        """
        Classify gesture using rule-based detection first, then CNN as fallback.
        Rule-based is more reliable for common gestures.
        IMPORTANT: Never trust CNN for thumbs_up - only use rule-based detection.
        """
        if landmarks is None or len(landmarks) == 0:
            return 'move_cursor', 0.0
        
        # Try rule-based detection first (more reliable)
        rule_gesture = self._detect_gesture_rules(landmarks)
        if rule_gesture is not None:
            return rule_gesture
        
        # Fallback to CNN if rule-based doesn't detect clear gesture
        cnn_gesture, cnn_confidence = self.gesture_cnn.predict(landmarks)
        
        # NEVER trust CNN for thumbs_up - it's too unreliable and causes accidental exits
        # Only use rule-based detection for thumbs_up
        if cnn_gesture == 'thumbs_up':
            # Ignore CNN thumbs_up detection, default to move_cursor
            return 'move_cursor', 0.5
        
        # Only trust CNN for other gestures if confidence is high enough
        if cnn_confidence > 0.7:
            return cnn_gesture, cnn_confidence
        
        # Default to move_cursor if nothing is clear
        return 'move_cursor', 0.5
    
    def _execute_action(self, gesture: str, position: Optional[Tuple[float, float]], 
                       frame_width: int = 640, frame_height: int = 480):
        """Execute mouse action based on gesture."""
        current_time = time.time()
        
        # Cooldown to prevent rapid repeated actions
        if gesture == self.last_gesture and (current_time - self.last_gesture_time) < self.gesture_cooldown:
            return
        
        if gesture == 'move_cursor':
            if position:
                self.mouse_controller.move_cursor(position[0], position[1], frame_width, frame_height)
        
        elif gesture == 'left_click':
            self.mouse_controller.left_click()
            self.last_gesture = gesture
            self.last_gesture_time = current_time
        
        elif gesture == 'right_click':
            self.mouse_controller.right_click()
            self.last_gesture = gesture
            self.last_gesture_time = current_time
            
        elif gesture == 'double_click':
            self.mouse_controller.double_click()
            self.last_gesture = gesture
            self.last_gesture_time = current_time
            
        elif gesture == 'middle_click':
            self.mouse_controller.middle_click()
            self.last_gesture = gesture
            self.last_gesture_time = current_time
            
        elif gesture == 'screenshot':
            self.mouse_controller.screenshot()
            self.last_gesture = gesture
            self.last_gesture_time = current_time
        
        elif gesture == 'scroll':
            # Scroll based on hand vertical movement. If position is provided, perform
            # continuous scrolling proportional to vertical delta. Otherwise perform a single step.
            if position:
                # position is normalized (0-1), y increases downward
                y = position[1]
                if self.last_scroll_pos is None:
                    self.last_scroll_pos = y
                dy = self.last_scroll_pos - y  # positive if hand moved up
                # Convert to scroll units (sensitivity tuned experimentally)
                scroll_amount = int(dy * self.scroll_sensitivity)
                # Apply a minimum threshold to avoid jitter
                if abs(scroll_amount) >= 1:
                    direction = 'up' if scroll_amount > 0 else 'down'
                    self.mouse_controller.scroll(direction, abs(scroll_amount))
                    # update last_scroll_pos only when scrolling to accumulate movement
                    self.last_scroll_pos = y
            else:
                # Discrete scroll step when no continuous position provided
                self.mouse_controller.scroll('up', 5)
                self.last_gesture = gesture
                self.last_gesture_time = current_time
        
        elif gesture == 'drag':
            if position:
                if not self.drag_active:
                    self.mouse_controller.start_drag(position[0], position[1], frame_width, frame_height)
                    self.drag_active = True
                else:
                    self.mouse_controller.update_drag(position[0], position[1], frame_width, frame_height)
            else:
                if self.drag_active:
                    self.mouse_controller.end_drag()
                    self.drag_active = False
        
        # DISABLED: Thumbs up gesture exit - only allow Q key or voice command
        # elif gesture == 'thumbs_up' or gesture == 'exit':
        #     # Exit gesture handling disabled to prevent accidental exits
        #     pass
        
        # Check for voice commands
        voice_cmd = self.voice_processor.get_command()
        if voice_cmd:
            if voice_cmd == 'exit':
                self.running = False
            elif voice_cmd == 'left_click':
                self.mouse_controller.left_click()
            elif voice_cmd == 'right_click':
                self.mouse_controller.right_click()
            elif voice_cmd == 'double_click':
                self.mouse_controller.double_click()
            elif voice_cmd == 'middle_click':
                self.mouse_controller.middle_click()
            elif voice_cmd == 'scroll_up':
                self.mouse_controller.scroll('up', 3)
            elif voice_cmd == 'scroll_down':
                self.mouse_controller.scroll('down', 3)
            elif voice_cmd == 'screenshot':
                self.mouse_controller.screenshot()
            elif voice_cmd == 'copy':
                self.mouse_controller.copy()
            elif voice_cmd == 'paste':
                self.mouse_controller.paste()
            elif voice_cmd == 'drag_start':
                pos = self.mouse_controller.get_cursor_position()
                self.mouse_controller.start_drag(pos[0], pos[1], self.mouse_controller.screen_width, self.mouse_controller.screen_height)
                self.drag_active = True
            elif voice_cmd == 'drag_stop':
                self.mouse_controller.end_drag()
                self.drag_active = False
    
    def run(self):
        """Main loop."""
        if not self.initialize():
            return
        
        self.running = True
        print("Gesture Mouse System started. Press 'Q' key to quit.")
        print("Note: Exit gesture (thumbs up) is disabled. Use 'Q' key or say 'exit' to quit.")
        print("Voice commands: 'left click', 'right click', 'scroll up', 'scroll down', 'exit'")
        
        frame_count = 0
        fps_start_time = time.time()
        # Throttling for processing heavy detection steps
        last_process_time = 0.0
        processed_count = 0
        
        try:
            while self.running:
                # Get frame
                frame = self.hand_tracker.get_frame()
                if frame is None:
                    break
                
                frame_height, frame_width = frame.shape[:2]

                now = time.time()
                # Throttle detection/classification to target_fps to improve processing performance
                if (now - last_process_time) >= (1.0 / self.target_fps):
                    last_process_time = now
                    processed_count += 1

                    # Detect hand
                    if self.mode == 'hand':
                        landmarks, annotated_frame = self.hand_tracker.detect_hand(frame)

                        if landmarks:
                            # Classify gesture
                            gesture, confidence = self._classify_gesture(landmarks)

                            # Get hand position
                            position = self._get_hand_position(landmarks, frame_width, frame_height)

                            # Always move cursor when hand is detected
                            if position:
                                self.mouse_controller.move_cursor(position[0], position[1], frame_width, frame_height)

                            # Execute gesture-specific actions with moderate confidence
                            if confidence > 0.4 and gesture != 'move_cursor':
                                self._execute_action(gesture, position, frame_width, frame_height)

                            # Display info
                            color = (0, 255, 0) if confidence > 0.4 else (0, 165, 255) if confidence > 0.3 else (0, 0, 255)
                            cv2.putText(annotated_frame, f"Gesture: {gesture} ({confidence:.2f})",
                                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

                            if position:
                                cv2.putText(annotated_frame, f"Position: ({position[0]:.2f}, {position[1]:.2f})",
                                           (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                                status_color = (0, 255, 0) if confidence > 0.6 else (0, 165, 255)
                                status_text = "ACTIVE" if confidence > 0.6 and gesture != 'move_cursor' else "TRACKING"
                                cv2.putText(annotated_frame, f"Cursor: {status_text}",
                                           (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.5, status_color, 1)
                        else:
                            annotated_frame = frame.copy()
                            cv2.putText(annotated_frame, "No hand detected",
                                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    else:
                        centroid, annotated_frame = self.hand_tracker.detect_hand(frame)
                        if centroid:
                            position = self._get_glove_position(centroid, frame_width, frame_height)
                            self.mouse_controller.move_cursor(position[0], position[1], frame_width, frame_height)
                            cv2.putText(annotated_frame, "Glove detected",
                                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        else:
                            annotated_frame = frame.copy()
                            cv2.putText(annotated_frame, "No glove detected",
                                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                else:
                    # Skip processing this frame; reuse last annotated_frame if available
                    try:
                        annotated_frame
                    except NameError:
                        annotated_frame = frame
                
                # Check for keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                
                # Display processing FPS (based on processed frames)
                frame_count += 1
                if processed_count > 0 and (processed_count % 30) == 0:
                    fps = processed_count / (time.time() - fps_start_time)
                    fps_start_time = time.time()
                    processed_count = 0
                    print(f"Processing FPS: {fps:.2f} (target {self.target_fps})")
                
                # Show frame
                cv2.imshow('Gesture Mouse', annotated_frame)
        
        except KeyboardInterrupt:
            print("\nInterrupted by user")
        
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources."""
        print("Cleaning up...")
        self.running = False
        self.mouse_controller.end_drag()
        self.voice_processor.stop_listening()
        self.hand_tracker.release()
        cv2.destroyAllWindows()
        print("Cleanup complete")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Gesture Controlled Virtual Mouse')
    parser.add_argument('--mode', type=str, default='hand', 
                       choices=['hand', 'glove'],
                       help='Tracking mode: hand (MediaPipe) or glove (OpenCV)')
    parser.add_argument('--model', type=str, default='models/gesture_cnn.h5',
                       help='Path to trained CNN model')
    parser.add_argument('--target-fps', type=int, default=30,
                        help='Target processing FPS for detection/classification (e.g. 30 or 60)')
    
    args = parser.parse_args()
    
    # Create and run system
    system = GestureMouseSystem(mode=args.mode, model_path=args.model, target_fps=args.target_fps)
    system.run()


if __name__ == '__main__':
    main()

