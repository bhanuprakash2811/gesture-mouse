"""
Unit tests for hand tracking module.
"""
import unittest
import numpy as np
from src.hand_tracking import HandTracker


class TestHandTracker(unittest.TestCase):
    """Test cases for HandTracker class."""
    
    def test_initialization_hand_mode(self):
        """Test initialization in hand mode."""
        tracker = HandTracker(mode='hand')
        self.assertEqual(tracker.mode, 'hand')
        self.assertIsNotNone(tracker.mp_hands)
        self.assertIsNotNone(tracker.hands)
    
    def test_initialization_glove_mode(self):
        """Test initialization in glove mode."""
        tracker = HandTracker(mode='glove')
        self.assertEqual(tracker.mode, 'glove')
        self.assertIsNone(tracker.mp_hands)
        self.assertIsNone(tracker.hands)
    
    def test_glove_color_setting(self):
        """Test setting glove color."""
        tracker = HandTracker(mode='glove')
        tracker.set_glove_color('blue')
        # Check that HSV bounds are set (basic check)
        self.assertIsNotNone(tracker.hsv_lower)
        self.assertIsNotNone(tracker.hsv_upper)


if __name__ == '__main__':
    unittest.main()

