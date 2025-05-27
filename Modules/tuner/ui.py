from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QFont
import numpy as np
import sounddevice as sd
import threading

from Modules.tuner.TunerObject import NoteFinder
from Modules.Parametres.logic import load_background, draw_background
from AudioSettingsManager import AudioSettingsManager
from config import theme_manager
from core.styles import retro_label_font, bpm_label_style


class renderArea(QWidget):
    def __init__(self):
        super().__init__()

        self.noteTool = NoteFinder()
        self.noteHeard = False

        # --- UI Setup ---
        self.LabelNote = QLabel("A4")
        self.LabelNote.setFont(retro_label_font(110))
        self.LabelNote.setAlignment(Qt.AlignCenter)
        self.LabelNote.setStyleSheet(bpm_label_style())

        self.Layout = QVBoxLayout()
        self.Layout.setContentsMargins(0, 30, 0, 0)
        self.Layout.addSpacing(20)
        self.Layout.addWidget(self.LabelNote)
        self.Layout.addStretch(1)
        self.setLayout(self.Layout)

        self.image = load_background()
        theme_manager.theme_changed.connect(self.update_background)

        # --- Tuner Stability ---
        self.lastStableNote = ""
        self.stabilityCounter = 0
        self.requiredStability = 3

        # --- Audio Thread ---
        self.running = True
        self.audio_thread = threading.Thread(target=self.listen_micro, daemon=True)
        self.audio_thread.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        draw_background(self, painter, self.image)

        y_offset = -50
        painter.setRenderHint(QPainter.Antialiasing)

        # Bars
        bar_positions = [120, 185, 250, 315, 380]
        pen = QPen(QColor("#403F4C"), 12)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)

        for x in bar_positions:
            painter.drawLine(x, 248 + y_offset, x, 288 + y_offset)

        # Tuning indicator
        ecart = max(-0.5, min(0.5, self.noteTool.currentEcart))
        center_x = self.width() // 2
        pixel_offset = ecart * 200
        indicator_x = int(center_x + pixel_offset)
        indicator_y = int(268 + y_offset)

        if self.noteHeard:
            painter.setOpacity(0.25)
            color = "#2ecc71" if abs(ecart) < 0.1 else "#e74c3c"
            painter.setBrush(QColor(color))
            painter.setPen(Qt.NoPen)
            painter.drawRect(self.rect())
            painter.setOpacity(1.0)

        brush = QBrush(QColor("#403F4C"))
        painter.setBrush(brush)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(indicator_x - 8, indicator_y - 8, 16, 16)

        self.noteHeard = False

    def mousePressEvent(self, event):
        from numpy.random import random
        self.noteHeard = True
        self.noteTool.currentEcart = random() - 0.5
        self.LabelNote.setText(self.noteTool.currentNote + str(self.noteTool.currentOrdre))
        self.repaint()

    def listen_micro(self):
        def callback(indata, frames, time, status):
            signal = indata[:, 0]
            if np.max(np.abs(signal)) < 0.005:
                return

            self.noteTool.getNote(44100, signal)
            note = self.noteTool.currentNote + str(self.noteTool.currentOrdre)

            if note == self.lastStableNote:
                self.stabilityCounter += 1
            else:
                self.stabilityCounter = 0
                self.lastStableNote = note

            if self.stabilityCounter >= self.requiredStability:
                self.LabelNote.setText(note)
                self.noteHeard = True
                self.repaint()
                self.stabilityCounter = 0

        try:
            device_index = AudioSettingsManager.get_input_device()
            with sd.InputStream(callback=callback, channels=1, samplerate=44100,
                                blocksize=4096, device=device_index):
                while self.running:
                    sd.sleep(100)
        except Exception as e:
            print("Microphone error:", e)

    def closeEvent(self, event):
        self.running = False
        self.audio_thread.join()
        event.accept()

    def update_background(self):
        self.image = load_background()
        self.update()
