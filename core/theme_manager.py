# core/theme_manager.py
from PyQt5.QtCore import QObject, pyqtSignal, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel

class ThemeManager(QObject):
    theme_changed = pyqtSignal()
    _instance = None
    dark_mode = False  # Define dark_mode as a class attribute

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ThemeManager, cls).__new__(cls)
            cls._instance._theme = "light"
        return cls._instance

    def toggle_dark_mode(self):
        """Toggle between light and dark mode."""
        ThemeManager.dark_mode = not ThemeManager.dark_mode
        self.theme_changed.emit()

    def is_dark_mode(self):
        """Check if dark mode is enabled."""
        return ThemeManager.dark_mode

    def get_background_path(self):
        """Get the background image path based on the current theme."""
        from config import BGList  # Lazy import to avoid circular dependency
        return BGList[1] if ThemeManager.dark_mode else BGList[0]