from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QSpacerItem, QSizePolicy
from PyQt5.QtMultimedia import QSoundEffect
from PyQt5.QtCore import Qt, QUrl, QTimer
from PyQt5.QtGui import QPainter, QColor, QFont
import os

from Modules.metronome.logic import Timer
import Modules.metronome.config as cfg
from Modules.Parametres.logic import load_background, draw_background

import config as config
from config import theme_manager
class MetronomeScreen(QWidget):
    def __init__(self):
        super().__init__()

        self.bpm = cfg.BPM_DEFAULT
        self.image = load_background()

        # --- BPM Label ---
        self.label = QLabel(f"BPM : {self.bpm}")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("""
            font-size: 42px;
            font-weight: bold;
            color: #2C3E50;
            padding-bottom: 10px;
        """)

        # --- Layout ---
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        layout.addWidget(self.label, alignment=Qt.AlignCenter)
        layout.addSpacerItem(QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Fixed))
        layout.addSpacerItem(QSpacerItem(20, 70, QSizePolicy.Minimum, QSizePolicy.Expanding))  # Balance bottom

        self.setLayout(layout)

        # --- Pulse Indicator ---
        self.pulse_radius = 0
        self.pulse_grow = True
        self.pulse_color = QColor("#5d8271")

        self.pulse_timer = QTimer()
        self.pulse_timer.setInterval(16)  # ~60 FPS
        self.pulse_timer.timeout.connect(self.update_pulse)

        # --- Sound ---
        self.sound = QSoundEffect()
        self.sound.setSource(QUrl.fromLocalFile(os.path.join("Assets", "tic.wav")))
        self.sound.setVolume(0.8)

        # --- Metronome ---
        self.metronome = Timer(bpm=self.bpm)
        self.metronome.tick.connect(self.play_tick)
        self.metronome.timer.stop()

        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()
        
        # --- Listen for Theme Changes ---
        theme_manager.theme_changed.connect(self.update_background)

    def toggle_theme(self):
        theme_manager.toggle_theme()

    def update_background(self):
        self.image = load_background()
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

    # Ensure the background image is scaled and centered
    draw_background(self, painter, self.image)

    # Draw the pulse indicator
    if self.metronome.timer.isActive():
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(self.pulse_color)
        painter.setPen(Qt.NoPen)

        # Draw pulse dot just below the label
        center_x = self.width() // 2
        center_y = self.height() // 2 + 40
        r = self.pulse_radius
        painter.drawEllipse(center_x - r, center_y - r, r * 2, r * 2)