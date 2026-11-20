"""
Mouse control module with cursor smoothing and gesture actions.
"""
from collections import deque
from typing import List, Optional, Tuple
import time

import numpy as np
import pyautogui

from src.utils import get_screen_resolution


class MouseController:
    """Control mouse cursor and actions with advanced smoothing."""

    def __init__(
        self,
        smoothing_alpha: float = 0.95,
        window_size: int = 2,
        interpolation_steps: int = 0,
        max_jump_distance: float = 100.0,
    ):
        self.smoothing_alpha = smoothing_alpha
        self.window_size = window_size
        self.interpolation_steps = interpolation_steps
        self.max_jump_distance = max_jump_distance

        self.position_buffer = deque(maxlen=window_size)
        self.previous_smoothed = None
        self.previous_position = None
        self.last_update_time = time.time()
        self.screen_width, self.screen_height = get_screen_resolution()
        self.is_dragging = False
        self.drag_start = None

        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0.0

    def _filter_outlier(
        self,
        new_pos: Tuple[float, float],
        previous_pos: Optional[Tuple[float, float]],
    ) -> Tuple[float, float]:
        """Filter isolated, implausibly large cursor jumps."""
        if previous_pos is None:
            return new_pos

        distance = np.sqrt(
            (new_pos[0] - previous_pos[0]) ** 2
            + (new_pos[1] - previous_pos[1]) ** 2
        )
        if distance > self.max_jump_distance:
            self.outlier_count = getattr(self, "outlier_count", 0) + 1
            if self.outlier_count < 5:
                return previous_pos
            self.outlier_count = 0
        else:
            self.outlier_count = 0
        return new_pos

    def _moving_average(
        self, positions: List[Tuple[float, float]]
    ) -> Tuple[float, float]:
        """Calculate the moving average of recent positions."""
        if not positions:
            return (0, 0)
        avg_x = np.mean([position[0] for position in positions])
        avg_y = np.mean([position[1] for position in positions])
        return (avg_x, avg_y)

    def _exponential_moving_average(
        self,
        current: Tuple[float, float],
        previous: Optional[Tuple[float, float]],
    ) -> Tuple[float, float]:
        """Apply exponential moving average smoothing."""
        if previous is None:
            return current
        x = self.smoothing_alpha * current[0] + (1 - self.smoothing_alpha) * previous[0]
        y = self.smoothing_alpha * current[1] + (1 - self.smoothing_alpha) * previous[1]
        return (x, y)

    def _interpolate(
        self,
        start: Tuple[float, float],
        end: Tuple[float, float],
        t: float,
    ) -> Tuple[float, float]:
        """Linearly interpolate between two cursor positions."""
        x = start[0] + (end[0] - start[0]) * t
        y = start[1] + (end[1] - start[1]) * t
        return (x, y)

    def move_cursor(
        self,
        x: float,
        y: float,
        frame_width: int = 640,
        frame_height: int = 480,
    ):
        """Move the cursor from normalized or frame-pixel coordinates."""
        if x is None or y is None:
            return

        try:
            fx = float(x)
            fy = float(y)
        except (TypeError, ValueError):
            return

        current_time = time.time()
        if fx <= 1.0 and fy <= 1.0:
            margin = 0.05
            fx = (fx - margin) / (1.0 - 2 * margin)
            fy = (fy - margin) / (1.0 - 2 * margin)
            fx = float(np.clip(fx, 0.0, 1.0))
            fy = float(np.clip(fy, 0.0, 1.0))
            screen_x = fx * self.screen_width
            screen_y = fy * self.screen_height
        else:
            screen_x = fx / frame_width * self.screen_width
            screen_y = fy / frame_height * self.screen_height

        screen_x = float(np.clip(screen_x, 0, max(0, self.screen_width - 1)))
        screen_y = float(np.clip(screen_y, 0, max(0, self.screen_height - 1)))
        current_pos = (screen_x, screen_y)

        filtered_pos = self._filter_outlier(current_pos, self.previous_position)
        self.position_buffer.append(filtered_pos)
        moving_average = self._moving_average(list(self.position_buffer))
        smoothed_pos = self._exponential_moving_average(
            moving_average, self.previous_smoothed
        )

        if (
            not np.isfinite(smoothed_pos[0])
            or not np.isfinite(smoothed_pos[1])
            or smoothed_pos[0] < 0
            or smoothed_pos[1] < 0
        ):
            return

        try:
            pyautogui.moveTo(
                int(smoothed_pos[0]), int(smoothed_pos[1]), duration=0.0
            )
        except Exception as exc:
            print(f"Error moving cursor: {exc}")

        self.previous_position = filtered_pos
        self.previous_smoothed = smoothed_pos
        self.last_update_time = current_time

    def left_click(self):
        """Perform a left click."""
        try:
            pyautogui.click(button="left")
            print("Left click performed")
        except Exception as exc:
            print(f"Error performing left click: {exc}")

    def right_click(self):
        """Perform a right click."""
        try:
            pyautogui.click(button="right")
            print("Right click performed")
        except Exception as exc:
            print(f"Error performing right click: {exc}")

    def double_click(self):
        """Perform a double click."""
        try:
            pyautogui.doubleClick()
            print("Double click performed")
        except Exception as exc:
            print(f"Error performing double click: {exc}")

    def middle_click(self):
        """Perform a middle click."""
        try:
            pyautogui.click(button="middle")
            print("Middle click performed")
        except Exception as exc:
            print(f"Error performing middle click: {exc}")

    def copy(self):
        """Send Ctrl+C."""
        try:
            pyautogui.hotkey("ctrl", "c")
            print("Copy performed")
        except Exception as exc:
            print(f"Error performing copy: {exc}")

    def paste(self):
        """Send Ctrl+V."""
        try:
            pyautogui.hotkey("ctrl", "v")
            print("Paste performed")
        except Exception as exc:
            print(f"Error performing paste: {exc}")

    def scroll(self, direction: str = "up", amount: int = 3):
        """Scroll the mouse wheel."""
        try:
            pyautogui.scroll(amount if direction == "up" else -amount)
            print(f"Scrolled {direction}")
        except Exception as exc:
            print(f"Error scrolling: {exc}")

    def screenshot(self, save_path: Optional[str] = None) -> Optional[str]:
        """Save a screenshot under screenshots/ unless a path is supplied."""
        try:
            import os
            from datetime import datetime

            os.makedirs("screenshots", exist_ok=True)
            if save_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_path = os.path.join("screenshots", f"screenshot_{timestamp}.png")
            pyautogui.screenshot(save_path)
            print(f"Screenshot saved to {save_path}")
            return save_path
        except Exception as exc:
            print(f"Error taking screenshot: {exc}")
            return None

    def start_drag(
        self,
        x: float,
        y: float,
        frame_width: int = 640,
        frame_height: int = 480,
    ):
        """Start a left-button drag."""
        if x <= 1.0 and y <= 1.0:
            screen_x = x * self.screen_width
            screen_y = y * self.screen_height
        else:
            screen_x = x / frame_width * self.screen_width
            screen_y = y / frame_height * self.screen_height

        try:
            pyautogui.mouseDown(button="left")
            self.is_dragging = True
            self.drag_start = (screen_x, screen_y)
            print("Drag started")
        except Exception as exc:
            print(f"Error starting drag: {exc}")

    def update_drag(
        self,
        x: float,
        y: float,
        frame_width: int = 640,
        frame_height: int = 480,
    ):
        """Move the cursor during a drag."""
        if self.is_dragging:
            self.move_cursor(x, y, frame_width, frame_height)

    def end_drag(self):
        """Release the left mouse button after a drag."""
        if not self.is_dragging:
            return
        try:
            pyautogui.mouseUp(button="left")
            self.is_dragging = False
            self.drag_start = None
            print("Drag ended")
        except Exception as exc:
            print(f"Error ending drag: {exc}")

    def get_cursor_position(self) -> Tuple[int, int]:
        """Get the current cursor position."""
        return pyautogui.position()
