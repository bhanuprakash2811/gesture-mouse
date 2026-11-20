"""
Voice command recognition module using SpeechRecognition and PyAudio.
"""
import speech_recognition as sr
import threading
import queue
import time
from typing import Optional, Callable

# Try to detect PocketSphinx for offline fallback
try:
    import pocketsphinx  # type: ignore
    HAS_POCKETSPHINX = True
except Exception:
    HAS_POCKETSPHINX = False


class VoiceCommandProcessor:
    """Process voice commands for mouse control."""
    
    SUPPORTED_COMMANDS = {
        'left click': 'left_click',
        'right click': 'right_click',
        'double click': 'double_click',
        'middle click': 'middle_click',
        'scroll up': 'scroll_up',
        'scroll down': 'scroll_down',
        'screenshot': 'screenshot',
        'take screenshot': 'screenshot',
        'capture screen': 'screenshot',
        'copy': 'copy',
        'paste': 'paste',
        'drag start': 'drag_start',
        'drag stop': 'drag_stop',
        'release': 'drag_stop',
        'exit': 'exit',
        'quit': 'exit',
        'stop': 'exit'
    }
    
    def __init__(self, callback: Optional[Callable] = None, use_offline_fallback: bool = True):
        """
        Initialize voice command processor.
        
        Args:
            callback: Function to call when command is detected (command_name)
        """
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.callback = callback
        self.is_listening = False
        self.command_queue = queue.Queue()
        self.thread = None
        self.use_offline_fallback = use_offline_fallback and HAS_POCKETSPHINX
        if use_offline_fallback and not HAS_POCKETSPHINX:
            print("PocketSphinx not available: offline fallback disabled. Install 'pocketsphinx' to enable it.")
        
        # Initialize microphone
        try:
            self.microphone = sr.Microphone()
            # Adjust for ambient noise
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print("Microphone initialized successfully")
        except Exception as e:
            print(f"Error initializing microphone: {e}")
    
    def start_listening(self):
        """Start listening for voice commands in background thread."""
        if self.is_listening:
            return
        
        self.is_listening = True
        self.thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.thread.start()
    
    def stop_listening(self):
        """Stop listening for voice commands."""
        self.is_listening = False
        if self.thread:
            self.thread.join(timeout=1)
    
    def _listen_loop(self):
        """Background loop for listening to voice commands."""
        if self.microphone is None:
            return
        
        failure_count = 0
        while self.is_listening:
            try:
                with self.microphone as source:
                    # Listen for audio with timeout
                    # Allow slightly longer phrases to be captured
                    audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=3)
                
                try:
                    # Recognize speech using Google Speech Recognition
                    text = self.recognizer.recognize_google(audio).lower()
                    print(f"Recognized: {text}")

                    # Check for supported commands (improved parsing)
                    command = self._parse_command(text)
                    if command:
                        print(f"Parsed command: {command}")
                        self.command_queue.put(command)
                        if self.callback:
                            self.callback(command)
                
                except sr.UnknownValueError:
                    # Speech was unintelligible
                    pass
                except sr.RequestError as e:
                    # Network or service error contacting Google API
                    print(f"Could not request results from speech recognition service: {e}")
                    failure_count += 1

                    # Try offline PocketSphinx fallback if available
                    if self.use_offline_fallback:
                        try:
                            sphinx_text = self.recognizer.recognize_sphinx(audio).lower()
                            print(f"Offline Recognized (sphinx): {sphinx_text}")
                            command = self._parse_command(sphinx_text)
                            if command:
                                self.command_queue.put(command)
                                if self.callback:
                                    self.callback(command)
                            # reset failure count on success
                            failure_count = 0
                        except Exception as sph_err:
                            print(f"PocketSphinx recognition failed: {sph_err}")
                    else:
                        # If no offline fallback, pause briefly before retrying to avoid spamming
                        time.sleep(1)
                        # After several consecutive failures, stop attempting to contact service
                    if failure_count >= 5:
                        print("Repeated failures contacting speech service - voice recognition paused.")
                        self.is_listening = False
            
            except sr.WaitTimeoutError:
                # Timeout - continue listening
                continue
            except Exception as e:
                print(f"Error in voice listening loop: {e}")
                break
    
    def _parse_command(self, text: str) -> Optional[str]:
        """
        Parse recognized text to find command.
        
        Returns:
            Command name or None
        """
        text = text.lower().strip()

        # Direct exact match
        if text in self.SUPPORTED_COMMANDS:
            return self.SUPPORTED_COMMANDS[text]

        # Keyword-based parsing for more robust matching
        # Scroll up / down
        if 'scroll' in text:
            # Check for modifiers (fast/quick/slow)
            modifier_fast = any(k in text for k in ('fast', 'quick', 'fastly', 'rapid'))
            modifier_slow = any(k in text for k in ('slow', 'gently', 'small'))
            if 'up' in text or 'scroll up' in text:
                if modifier_fast:
                    return 'scroll_up_fast'
                if modifier_slow:
                    return 'scroll_up_slow'
                return 'scroll_up'
            if 'down' in text or 'scroll down' in text:
                if modifier_fast:
                    return 'scroll_down_fast'
                if modifier_slow:
                    return 'scroll_down_slow'
                return 'scroll_down'

        # Clicks
        if 'double' in text and 'click' in text:
            return 'double_click'
        if 'middle' in text and 'click' in text:
            return 'middle_click'
        if 'left' in text and 'click' in text:
            return 'left_click'
        if 'right' in text and 'click' in text:
            return 'right_click'

        # Screenshot / capture
        if ('screenshot' in text) or ('screen shot' in text) or ('capture' in text) or ('take screenshot' in text) or ('take a screenshot' in text):
            return 'screenshot'
            
        # Dragging
        if 'drag' in text and 'start' in text:
            return 'drag_start'
        if ('drag' in text and 'stop' in text) or 'release' in text:
            return 'drag_stop'
            
        # Clipboard
        if 'copy' in text:
            return 'copy'
        if 'paste' in text:
            return 'paste'

        # Check for supported command keywords
        for key, value in self.SUPPORTED_COMMANDS.items():
            if key in text:
                return value

        return None
    
    def get_command(self, timeout: float = 0.1) -> Optional[str]:
        """
        Get next command from queue (non-blocking).
        
        Args:
            timeout: Timeout in seconds
        
        Returns:
            Command name or None
        """
        try:
            return self.command_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def listen_once(self) -> Optional[str]:
        """
        Listen for a single command (blocking).
        
        Returns:
            Command name or None
        """
        if self.microphone is None:
            return None
        
        try:
            with self.microphone as source:
                print("Listening for command...")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=3)
            
            try:
                text = self.recognizer.recognize_google(audio).lower()
                print(f"Recognized: {text}")
                return self._parse_command(text)
            except sr.UnknownValueError:
                print("Could not understand audio")
                return None
            except sr.RequestError as e:
                print(f"Error with speech recognition service: {e}")
                return None
        
        except Exception as e:
            print(f"Error listening: {e}")
            return None

