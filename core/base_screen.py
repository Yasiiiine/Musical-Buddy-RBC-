# core/base_screen.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPixmap
from config import theme_manager

class BaseScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        theme_manager.theme_changed.connect(self.update_background)
        self.setAttribute(Qt.WA_StyledBackground, True)

    def update_background(self):
        self.update()

    def refresh_background(self):
        self.image_label.setPixmap(QPixmap(theme_manager.get_background_path()))


    def paintEvent(self, event):
        painter = QPainter(self)
