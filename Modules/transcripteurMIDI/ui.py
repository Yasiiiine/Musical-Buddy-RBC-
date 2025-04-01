# ui.py

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt

import Modules.transcripteurMIDI.config as cfg

class Module5Screen(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        label = QLabel(cfg.MODULE_LABEL)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 32px; font-weight: bold;")

        layout.addWidget(label)
        self.setLayout(layout)
        self.setStyleSheet(f"background-color: {cfg.MODULE_COLOR};")
