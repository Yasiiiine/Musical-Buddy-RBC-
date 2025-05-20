from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter

import Modules.Parametres.config as cfg
from Modules.Parametres.logic import load_background, draw_background
import config as config

from config import theme_manager

class Module7Screen(QWidget):
    def __init__(self):
        super().__init__()

        # --- Label Setup ---
        self.label = QLabel(cfg.MODULE_LABEL)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 32px; font-weight: bold; color: white;")

        # --- Layout ---
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        # --- Background Image ---
        self.image = load_background()
        self.toggle_button = QPushButton("Toggle Theme")
        self.toggle_button.clicked.connect(self.toggle_theme)
        self.toggle_button.setStyleSheet("""
            QPushButton {
                background-color: #5d8271;
                color: white;
                font-size: 20px;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #4a6b5c;
            }
        """)
        layout.addWidget(self.toggle_button)

        # --- Listen for Theme Changes ---
        theme_manager.theme_changed.connect(self.update_background)

        # --- Focus (optional) ---
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

    def toggle_theme(self):
        theme_manager.toggle_theme()

    def update_background(self):
        self.image = load_background()
        self.update()

    def paintEvent(self, event):
        """Override paintEvent to draw the background."""
        painter = QPainter(self)
        draw_background(self, painter, self.image)