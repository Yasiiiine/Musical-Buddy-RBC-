from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter

import Modules.Parametres.config as cfg
from Modules.Parametres.logic import load_background, draw_background
import config as config

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
        layout.addWidget(self.toggle_button)

        # --- Focus (optional) ---
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

    def toggle_theme(self):
        # Switch the theme
        config.theme = 'dark' if config.theme == 'light' else 'light'
        # Reload the background
        self.image = load_background()
        # Update the UI
        self.update()

    def start(self):
        """Start screen logic (called when switching to this screen)."""
        pass  # Fade handled by MainWindow

