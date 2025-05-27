from PyQt5.QtCore import QObject, pyqtSignal

class ThemeManager(QObject):
    theme_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.theme = 'light'

    def toggle_theme(self):
        self.theme = 'dark' if self.theme == 'light' else 'light'
        self.theme_changed.emit()