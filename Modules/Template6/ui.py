from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
from Modules.Template6.logic import MusicPlayer
import Modules.Template6.config as cfg

class Module6Screen(QWidget):
    def __init__(self):
        super().__init__()

        self.player = MusicPlayer()
        self.label = QLabel("Appuyez sur la touche E pour jouer de la musique")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 32px; font-weight: bold;")

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.setStyleSheet(f"background-color: {cfg.MODULE_COLOR};")

        self.setFocusPolicy(Qt.StrongFocus)  # Important pour capter les touches
        self.setFocus()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_E:
            if not self.player.is_playing():
                self.player.play("Staying Alive")
                self.label.setText("🎵 Lecture de la musique... (E pour stopper)")
            else:
                self.player.stop()
                self.label.setText("Appuyez sur la touche E pour jouer de la musique")