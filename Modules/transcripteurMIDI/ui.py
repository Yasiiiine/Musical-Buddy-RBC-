# ui.py

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPainter
import config

import Modules.transcripteurMIDI.config as cfg
from Modules.Parametres.logic import load_background, draw_background

class Module5Screen(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        label = QLabel(cfg.MODULE_LABEL)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 32px; font-weight: bold;")

        self.image = load_background()

        layout.addWidget(label)
        self.setLayout(layout)
