# ui.py

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPainter

<<<<<<< HEAD:Modules/Template5/ui.py
import Modules.Template5.config as cfg
from Modules.Parametres.logic import load_background, draw_background

=======
import Modules.transcripteurMIDI.config as cfg
>>>>>>> c4a8c1734b4ce66e60ebf5bf489e585919876e48:Modules/transcripteurMIDI/ui.py

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
    def paintEvent(self, event):
        painter = QPainter(self)
        draw_background(self, painter, self.image)
        super().paintEvent(event)