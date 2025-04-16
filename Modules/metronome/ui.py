from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtMultimedia import QSoundEffect
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QPainter
import os

from Modules.metronome.logic import Timer
import Modules.metronome.config as cfg
from Modules.Parametres.logic import load_background, draw_background


class MetronomeScreen(QWidget):
    def __init__(self):
        super().__init__()

        # --- Configuration ---
        self.bpm = cfg.BPM_DEFAULT
        self.image = load_background()

        # --- BPM Display Label ---
        self.label = QLabel(f"BPM : {self.bpm}")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 32px; font-weight: bold; color: white;")

        # --- Layout ---
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        # --- Sound Setup ---
        self.sound = QSoundEffect()
        self.sound.setSource(QUrl.fromLocalFile(os.path.join("Assets", "tic.wav")))
        self.sound.setVolume(0.8)

        # --- Metronome Timer ---
        self.metronome = Timer(bpm=self.bpm)
        self.metronome.tick.connect(self.play_tick)
        self.metronome.timer.stop()

        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

    def play_tick(self):
        """Play tick sound."""
        self.sound.play()

    def wheelEvent(self, event):
        """Scroll to adjust BPM."""
        delta = event.angleDelta().y() // 120
        self.bpm = max(cfg.BPM_MIN, min(cfg.BPM_MAX, self.bpm + delta))
        self.label.setText(f"BPM : {self.bpm}")
        self.metronome.set_bpm(self.bpm)

    def start(self):
        """Start the metronome."""
        self.metronome.timer.start()

    def stop(self):
        """Stop the metronome."""
        self.metronome.timer.stop()
