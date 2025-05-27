# core/base_screen.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPixmap
from core.theme_manager import ThemeManager
from Modules.Parametres.logic import load_background, draw_background

class BaseScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        self.image = load_background()

        ThemeManager().theme_changed.connect(self.update_background)
        self.setAttribute(Qt.WA_StyledBackground, True)

    def update_background(self):
        self.image = load_background()
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        draw_background(self, painter, self.image)
