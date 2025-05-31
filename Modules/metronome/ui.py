# modules/metronome/ui.py
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QSpacerItem, QSizePolicy
from PyQt5.QtMultimedia import QSoundEffect
from PyQt5.QtCore import Qt, QUrl, QTimer
from PyQt5.QtGui import QPainter, QColor, QFont, QPixmap

import os

from core.base_screen import BaseScreen
from Modules.metronome.logic import Timer
import Modules.metronome.config as cfg
from core.styles import retro_label_font, bpm_label_style


class MetronomeScreen(BaseScreen):
    def __init__(self):
        super().__init__()

        self.bpm = cfg.BPM_DEFAULT

        # --- BPM Label ---
        self.label = QLabel(f"BPM : {self.bpm}")
        self.label.setFont(retro_label_font(60))
        self.label.setStyleSheet(bpm_label_style())

        # --- Layout ---
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)
        self.layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.layout.addWidget(self.label, alignment=Qt.AlignCenter)
        self.layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))
        self.layout.addSpacerItem(QSpacerItem(20, 70, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # --- Pulse State ---
        self.pulse_radius = 0
        self.pulse_grow = True
        self.pulse_color = QColor("#5d8271")

        self.pulse_timer = QTimer()
        self.pulse_timer.setInterval(16)  # ~60 FPS
        self.pulse_timer.timeout.connect(self.update_pulse)

        # --- Sound Effect ---
        self.sound = QSoundEffect()
        self.sound.setSource(QUrl.fromLocalFile(os.path.join("Assets", "tic.wav")))
        self.sound.setVolume(0.8)

        # --- Metronome Logic ---
        self.metronome = Timer(bpm=self.bpm)
        self.metronome.tick.connect(self.play_tick)
        self.metronome.timer.stop()

        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()



    def update_background(self):
        self.update()

    def play_tick(self):
        self.sound.play()
        self.pulse_radius = 10
        self.pulse_grow = True
        self.update()

    def wheelEvent(self, event):
        delta = event.angleDelta().y() // 120
        self.bpm = max(cfg.BPM_MIN, min(cfg.BPM_MAX, self.bpm + delta))
        self.label.setText(f"BPM : {self.bpm}")
        self.metronome.set_bpm(self.bpm)

        # BPM edge warning color
        if self.bpm == cfg.BPM_MIN or self.bpm == cfg.BPM_MAX:
            self.pulse_color = QColor("#e74c3c")  # Red
        else:
            self.pulse_color = QColor("#5d8271")  # Green

    def start(self):
        self.metronome.timer.start()
        self.pulse_timer.start()

    def stop(self):
        self.metronome.timer.stop()
        self.pulse_timer.stop()

    def update_pulse(self):
        if self.pulse_grow:
            self.pulse_radius += 1
            if self.pulse_radius >= 18:
                self.pulse_grow = False
        else:
            self.pulse_radius = max(0, self.pulse_radius - 1)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)

        if self.metronome.timer.isActive():
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(self.pulse_color)
            painter.setPen(Qt.NoPen)
            cx = self.width() // 2
            cy = self.height() // 2 + 40
            r = self.pulse_radius
            painter.drawEllipse(cx - r, cy - r, r * 2, r * 2)