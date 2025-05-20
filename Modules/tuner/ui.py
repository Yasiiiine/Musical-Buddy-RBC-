# ui.py
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPen, QBrush, QPainter, QColor, QFont
from PyQt5.QtMultimedia import QAudioRecorder, QAudioProbe, QAudioInput
import Modules.tuner.config as cfg
from Modules.tuner.TunerObject import NoteFinder
from Modules.Parametres.logic import load_background, draw_background, update_background
import config
from config import theme_manager
import pyaudio
from AudioSettingsManager import AudioSettingsManager

from numpy.random import random
import sounddevice as sd
import numpy as np
import threading

class renderArea(QWidget):
    def __init__(self):
        super().__init__()

        self.noteTool = NoteFinder()
        self.noteHeard = False

        font = QFont("Arial", 60, QFont.Bold, italic=False)
        self.LabelNote = QLabel(text="A4")
        self.LabelNote.setFont(font)
        self.LabelNote.setAlignment(Qt.AlignCenter)
        self.LabelNote.setStyleSheet("""
            color: #2C3E50;
        """)

        self.Layout = QVBoxLayout()
        self.Layout.setContentsMargins(0, 30, 0, 0)

        self.Layout.addSpacing(20)
        self.Layout.addWidget(self.LabelNote)
        self.Layout.addStretch(1)

        self.image = load_background()
        self.setLayout(self.Layout)
        self.p = pyaudio.PyAudio()
        stream = self.p.open(44100,channels=1,format=pyaudio.paInt16,input=True,output=True,frames_per_buffer=1024*4)

        # Variables de stabilité
        self.lastStableNote = ""
        self.stabilityCounter = 0
        self.requiredStability = 3  # Plus c'est grand, plus c'est stable

        # Lancement thread micro
        self.running = True
        self.audio_thread = threading.Thread(target=self.listen_micro, daemon=True)
        self.audio_thread.start()

    def paintEvent(self, event):
        painter = QPainter(self)

        # Ensure the background image is scaled and centered
        draw_background(self, painter, self.image)

        # Draw the tuning indicator (existing logic)
        y_offset = -50
        pen = QPen(Qt.black)
        pen.setStyle(Qt.PenStyle.NoPen)
        painter.setPen(pen)

        brush = QBrush()
        painter.setBrush(brush)

        rect = self.size()
        rect.setWidth(rect.width() - 20)
        rect.setHeight(rect.height() - 20)

        painter.drawRect(self.x() + 10, self.y() + 10, rect.width(), rect.height())

        # Additional tuning indicator logic...
        pen.setColor(Qt.black)
        pen.setStyle(Qt.SolidLine)
        pen.setWidth(10)
        painter.setPen(pen)

        bar_positions = [120, 185, 250, 315, 380]
        bar_color = QColor("#403F4C")
        bar_width = 12

        pen = QPen(bar_color)
        pen.setWidth(bar_width)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)

        for x in bar_positions:
            painter.drawLine(x, 248 + y_offset, x, 288 + y_offset)

        self.noteHeard = False

        # Base values
        ecart = self.noteTool.currentEcart
        ecart = max(-0.5, min(0.5, ecart))  # Clamp between -0.5 and +0.5

        track_width = 200  # total width in pixels for full [-0.5, +0.5] range
        center_x = self.width() // 2

        # Convert ecart to pixels: -0.5 → -track_width/2, 0 → 0, +0.5 → +track_width/2
        pixel_offset = ecart * track_width
        indicator_x = int(center_x + pixel_offset)

        indicator_y = int(268 + y_offset)

        if self.noteHeard:
            if abs(self.noteTool.currentEcart - self.noteTool.currentEcart) < 0.1:
                painter.setOpacity(0.25)
                painter.setBrush(QColor("#2ecc71"))
                painter.setPen(Qt.NoPen)
                painter.drawRect(self.rect())
                painter.setOpacity(1.0)
            else:
                painter.setOpacity(0.25)
                painter.setBrush(QColor("#e74c3c"))
                painter.setPen(Qt.NoPen)
                painter.drawRect(self.rect())
                painter.setOpacity(1.0)

        brush.setStyle(Qt.BrushStyle.SolidPattern)
        brush.setColor(QColor("#403F4C"))
        painter.setBrush(brush)
        painter.setPen(Qt.PenStyle.SolidLine)
        painter.drawEllipse(indicator_x - 8, indicator_y - 8, 16, 16)
        print(self.noteTool.currentEcart)

    def mousePressEvent(self, a0):
        self.noteHeard = not self.noteHeard
        self.noteTool.currentEcart = (random() - 0.5)
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
            with sd.InputStream(callback=callback, channels=1, samplerate=44100, blocksize=4096, device=device_index) as stream:
                while self.running:
                    sd.sleep(100)
        except Exception as e:
            print("Erreur micro :", e)

    def closeEvent(self, event):
        self.running = False
        self.audio_thread.join()
        event.accept()

    def processBuffer():
        pass
