from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
import Modules.enregistrement.config as cfg
from Modules.enregistrement.logic import Recorder
from Modules.Parametres.logic import load_background, draw_background
from PyQt5.QtGui import QPixmap, QPainter

class Module3Screen(QWidget):
    def __init__(self):
        super().__init__()

        self.recorder = Recorder()

        self.label = QLabel("Appuyez sur la touche E pour enregistrer")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 18px; font-weight: bold;")

        self.image = load_background()

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()
    def paintEvent(self, event):
        painter = QPainter(self)
        draw_background(self, painter, self.image)
        super().paintEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_E:
            self.recorder.toggle_recording()
            if self.recorder.short_recording:
                self.label.setText("Enregistrement trop court!")
                self.recorder.short_recording = False
            elif self.recorder.recording:
                self.label.setText("Enregistrement en cours... (E pour stopper)")
            else:
                self.label.setText("Enregistrement sauvegardé ! Appuyez sur E pour recommencer.")