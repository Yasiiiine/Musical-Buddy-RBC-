from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPainter
from Modules.Template6.logic import MusicPlayer
from Modules.Parametres.logic import load_background, draw_background

import Modules.Template6.config as cfg

class Module6Screen(QWidget):
    def __init__(self):
        super().__init__()

        self.player = MusicPlayer()
        self.label = QLabel("Press E to play")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 32px; font-weight: bold;")

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.image = load_background()

        self.setFocusPolicy(Qt.StrongFocus)  # Important pour capter les touches
        self.setFocus()

    def paintEvent(self, event):
            painter = QPainter(self)
            draw_background(self, painter, self.image)
            super().paintEvent(event)
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_E:
            if not self.player.is_playing():
                self.player.play("Staying Alive")
                self.label.setText("🎵... (E to stop)")
            else:
                self.player.stop()
                self.label.setText("Press E to play")