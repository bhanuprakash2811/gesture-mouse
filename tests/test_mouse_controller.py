"""
Unit tests for mouse controller module.
"""
import unittest
from unittest.mock import patch, MagicMock
from src.mouse_controller import MouseController


class TestMouseController(unittest.TestCase):
    """Test cases for MouseController class."""
    
    def test_initialization(self):
        """Test MouseController initialization."""
        controller = MouseController(smoothing_alpha=0.7)
        self.assertEqual(controller.smoothing_alpha, 0.7)
        self.assertIsNone(controller.previous_position)
        self.assertIsNotNone(controller.screen_width)
        self.assertIsNotNone(controller.screen_height)
    
    @patch('src.mouse_controller.pyautogui')
    def test_left_click(self, mock_pyautogui):
        """Test left click."""
        controller = MouseController()
        controller.left_click()
        mock_pyautogui.click.assert_called_once_with(button='left')
    
    @patch('src.mouse_controller.pyautogui')
    def test_right_click(self, mock_pyautogui):
        """Test right click."""
        controller = MouseController()
        controller.right_click()
        mock_pyautogui.click.assert_called_once_with(button='right')
    
    @patch('src.mouse_controller.pyautogui')
    def test_scroll(self, mock_pyautogui):
        """Test scroll."""
        controller = MouseController()
        controller.scroll('up', 3)
        mock_pyautogui.scroll.assert_called_once_with(3)


if __name__ == '__main__':
    unittest.main()

