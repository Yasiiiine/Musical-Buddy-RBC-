# ui.py

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtMultimedia import QSoundEffect
from PyQt5.QtCore import Qt, QUrl, QTimer
import os
from Modules.metronome.logic import Timer
import Modules.metronome.config as cfg


class MetronomeScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.bpm = cfg.BPM_DEFAULT

        self.label = QLabel(f"BPM : {self.bpm}")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 32px; font-weight: bold;")

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)
        self.setStyleSheet(f"background-color: {cfg.BG_COLOR};")

        # Son tic
        self.sound = QSoundEffect()
        self.sound.setSource(QUrl.fromLocalFile(os.path.join("Assets", "tic.wav")))
        self.sound.setVolume(0.8)

        # Timer logique
        self.metronome = Timer(bpm=self.bpm)
        self.metronome.tick.connect(self.play_tick)
        self.metronome.timer.stop()  # Démarrage déclenché manuellement

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