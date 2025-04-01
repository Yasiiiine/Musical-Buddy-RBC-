from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtMultimedia import QSoundEffect
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QPixmap, QPainter
import os

from Modules.metronome.logic import Timer
import Modules.metronome.config as cfg
from Modules.Parametres.logic import load_background, draw_background

class MetronomeScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.bpm = cfg.BPM_DEFAULT

        self.label = QLabel(f"BPM : {self.bpm}")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 32px; font-weight: bold; color: white;")

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.image = load_background()

        self.sound = QSoundEffect()
        self.sound.setSource(QUrl.fromLocalFile(os.path.join("Assets", "tic.wav")))
        self.sound.setVolume(0.8)

        self.metronome = Timer(bpm=self.bpm)
        self.metronome.tick.connect(self.play_tick)
        self.metronome.timer.stop()

    def paintEvent(self, event):
        painter = QPainter(self)
        draw_background(self, painter, self.image)
        super().paintEvent(event)

    def play_tick(self):
        self.sound.play()

    def wheelEvent(self, event):
        delta = event.angleDelta().y() // 120
        self.bpm = max(cfg.BPM_MIN, min(cfg.BPM_MAX, self.bpm + delta))
        self.label.setText(f"BPM : {self.bpm}")
        self.metronome.set_bpm(self.bpm)

    def start(self):
        self.metronome.timer.start()

    def stop(self):
        self.metronome.timer.stop()
