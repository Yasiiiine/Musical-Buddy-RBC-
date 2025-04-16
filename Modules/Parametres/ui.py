from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter

import Modules.Parametres.config as cfg
from Modules.Parametres.logic import load_background, draw_background


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

        # --- Focus (optional) ---
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

    def start(self):
        """Start screen logic (called when switching to this screen)."""
        pass  # Fade handled by MainWindow

