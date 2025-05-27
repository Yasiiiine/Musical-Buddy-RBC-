# core/theme_manager.py
from PyQt5.QtCore import QObject, pyqtSignal, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel

class ThemeManager(QObject):
    theme_changed = pyqtSignal()
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ThemeManager, cls).__new__(cls)
            cls._instance._theme = "light"
        return cls._instance

    def toggle_theme(self):
        self._theme = "dark" if self._theme == "light" else "light"
        self.theme_changed.emit()

    def current_theme(self):
        return self._theme

    def get_background_path(self):
        return "Assets/BGDM.png" if self._theme == "dark" else "Assets/BGLM.png"