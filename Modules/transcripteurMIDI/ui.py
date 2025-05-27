# ui.py

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPainter
import config

import Modules.transcripteurMIDI.config as cfg
from core.styles import retro_label_font, bpm_label_style
from core.base_screen import BaseScreen
from core.theme_manager import ThemeManager
class Module5Screen(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        label = QLabel(cfg.MODULE_LABEL)
        label.setAlignment(Qt.AlignCenter)

        layout.addWidget(label)
        label.setFont(retro_label_font(32))
        label.setStyleSheet(bpm_label_style())
        self.setLayout(layout)
