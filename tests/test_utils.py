"""
Unit tests for utility functions.
"""
import unittest
import numpy as np
from src.utils import (
    extract_landmark_features,
    calculate_distances,
    exponential_moving_average,
    get_screen_resolution
)


class TestUtils(unittest.TestCase):
    """Test cases for utility functions."""
    
    def test_extract_landmark_features(self):
        """Test landmark feature extraction."""
        # Create mock landmarks
        class Landmark:
            def __init__(self, x, y, z):
                self.x = x
                self.y = y
                self.z = z
        
        landmarks = [Landmark(0.1 * i, 0.2 * i, 0.3 * i) for i in range(21)]
        features = extract_landmark_features(landmarks)
        
        self.assertEqual(len(features), 63)
        self.assertIsInstance(features, np.ndarray)
    
    def test_extract_landmark_features_empty(self):
        """Test with empty landmarks."""
        features = extract_landmark_features([])
        self.assertEqual(len(features), 63)
        self.assertTrue(np.all(features == 0))
    
    def test_exponential_moving_average(self):
        """Test exponential moving average."""
        current = (100, 200)
        previous = (90, 190)
        result = exponential_moving_average(current, previous, alpha=0.5)
        
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)
        # Should be between current and previous
        self.assertGreater(result[0], previous[0])
        self.assertLess(result[0], current[0])
    
    def test_exponential_moving_average_no_previous(self):
        """Test EMA with no previous value."""
        current = (100, 200)
        result = exponential_moving_average(current, None, alpha=0.5)
        self.assertEqual(result, current)
    
    def test_get_screen_resolution(self):
        """Test screen resolution retrieval."""
        width, height = get_screen_resolution()
        self.assertIsInstance(width, int)
        self.assertIsInstance(height, int)
        self.assertGreater(width, 0)
        self.assertGreater(height, 0)


if __name__ == '__main__':
    unittest.main()

