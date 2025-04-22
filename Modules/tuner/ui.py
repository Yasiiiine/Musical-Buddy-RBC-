# ui.py
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPen, QBrush, QPainter, QColor, QFont
from PyQt5.QtMultimedia import QAudioRecorder, QAudioProbe, QAudioInput
import Modules.tuner.config as cfg
from Modules.tuner.TunerObject import NoteFinder
from Modules.Parametres.logic import load_background, draw_background
import config

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

        # Variables de stabilité
        self.lastStableNote = ""
        self.stabilityCounter = 0
        self.requiredStability = 3  # Plus c'est grand, plus c'est stable

        # Lancement thread micro
        self.running = True
        self.audio_thread = threading.Thread(target=self.listen_micro)
        self.audio_thread.start()

    def paintEvent(self, event):
        painter = QPainter(self)
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

        if self.noteHeard:
            if abs(self.noteTool.currentEcart - round(self.noteTool.currentEcart)) < 0.1:
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

                indicator_x = round(((self.size().width() - 60) * ((1/2) + self.noteTool.currentEcart))) + 30
                indicator_y = 268 + y_offset

                brush.setColor(QColor("#E94F37"))
                painter.setBrush(brush)
                painter.setPen(Qt.NoPen)
                painter.drawEllipse(indicator_x - 8, indicator_y - 8, 16, 16)

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
            with sd.InputStream(callback=callback, channels=1, samplerate=44100, blocksize=4096, device=(1, None)):
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
