# ui.py
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from Modules.Template6.logic import MusicPlayer
from core.theme_manager import ThemeManager

class Module6Screen(QWidget):
    def __init__(self):
        super().__init__()

        self.player = MusicPlayer()

        self.label = QLabel("Press E to play")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 32px; font-weight: bold; color: #2C3E50;")
        self.label.setFont(QFont("Arial", 24, QFont.Bold))


        layout = QVBoxLayout()
        layout.setContentsMargins(40, 30, 40, 30)
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_E:
            if not self.player.is_playing():
                self.player.play("Dream theater the mirror")
                self.label.setText("Playing... (Press E to stop)")
            else:
                self.player.stop()
                self.label.setText("Press E to play")
        else:
            super().keyPressEvent(event)  # allow screen switching with other keys
