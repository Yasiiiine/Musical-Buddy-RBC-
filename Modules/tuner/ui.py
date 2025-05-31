# Modules/tuner/ui.py

from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor
import numpy as np
import sounddevice as sd
import threading

from Modules.tuner.TunerObject import NoteFinder
from AudioSettingsManager import AudioSettingsManager
from core.styles import retro_label_font, bpm_label_style


class NoteUpdateSignal(QObject):
    """
    A QObject subclass that simply carries a signal to pass
    updated note text and ecart from the worker thread to the GUI thread.
    """
    note_detected = pyqtSignal(str, float)


class renderArea(QWidget):
    def __init__(self):
        super().__init__()

        self.noteTool = NoteFinder()
        self.noteHeard = False
        self.current_ecart = 0.0

        # --- Label to display the recognized note ---
        self.LabelNote = QLabel("A4", self)
        self.LabelNote.setFont(retro_label_font(110))
        self.LabelNote.setAlignment(Qt.AlignCenter)
        self.LabelNote.setStyleSheet(bpm_label_style())

        # --- Layout: push label slightly down, then stretch ---
        self.Layout = QVBoxLayout(self)
        self.Layout.setContentsMargins(0, 0, 0, 0)
        self.Layout.addSpacing(150)             # vertical offset
        self.Layout.addWidget(self.LabelNote)
        self.Layout.addStretch(1)
        self.setLayout(self.Layout)

        # --- Prepare a signal object so worker thread can inform us on the GUI side ---
        self.signals = NoteUpdateSignal()
        self.signals.note_detected.connect(self.on_note_detected)

        # --- Tuner “hold‐steady” logic ---
        self.lastStableNote = ""
        self.stabilityCounter = 0
        self.requiredStability = 3            # require 3 consecutive matches

        # --- Launch microphone thread as a daemon, so it won’t block app exit ---
        self.running = True
        self.audio_thread = threading.Thread(target=self.listen_micro, daemon=True)
        self.audio_thread.start()

    def on_note_detected(self, note_str: str, ecart: float):
        """
        Slot, called in the GUI (main) thread whenever a stable note is detected.
        We update self.LabelNote, store ecart, set noteHeard=True, then schedule a repaint().
        """
        self.LabelNote.setText(note_str)
        self.current_ecart = ecart
        self.noteHeard = True
        # Schedule a repaint in the GUI thread
        self.update()

    def paintEvent(self, event):
        """
        Draw the five bars, the indicator dot, and a translucent overlay if a stable note was just detected.
        Runs in the GUI thread only.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Center coordinates
        center_x = self.width() // 2
        center_y = self.height() // 2 + 30

        # Draw five vertical bars, equally spaced around center_x
        bar_spacing = 65
        bar_positions = [
            center_x - 2 * bar_spacing,
            center_x - 1 * bar_spacing,
            center_x,
            center_x + 1 * bar_spacing,
            center_x + 2 * bar_spacing,
        ]
        bar_top = center_y - 20
        bar_bottom = center_y + 20

        pen = QPen(QColor("#403F4C"), 12)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)

        for x in bar_positions:
            painter.drawLine(x, bar_top, x, bar_bottom)

        # Compute dot offset (clamp ecart between -0.5 and +0.5, then map to ±200 px)
        ecart = max(-0.5, min(0.5, self.current_ecart))
        pixel_offset = ecart * 200
        indicator_x = int(center_x + pixel_offset)
        indicator_y = center_y

        # If a stable note was just detected, show translucent overlay
        if self.noteHeard:
            painter.setOpacity(0.25)
            color_hex = "#2ecc71" if abs(ecart) < 0.1 else "#e74c3c"
            painter.setBrush(QColor(color_hex))
            painter.setPen(Qt.NoPen)
            painter.drawRect(self.rect())
            painter.setOpacity(1.0)
            # Reset flag so overlay only draws once per detection
            self.noteHeard = False

        # Finally, draw the small indicator dot
        brush = QBrush(QColor("#403F4C"))
        painter.setBrush(brush)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(indicator_x - 8, indicator_y - 8, 16, 16)

    def mousePressEvent(self, event):
        """
        For manual testing: clicking anywhere simulates hearing a note,
        randomly offset, so indicator moves and label changes.
        """
        from numpy.random import random
        simulated_offset = random() - 0.5
        simulated_note = self.noteTool.currentNote + str(self.noteTool.currentOrdre)
        # We can directly call the slot, since it expects (note_str, ecart)
        self.on_note_detected(simulated_note, simulated_offset)

    def listen_micro(self):
        """
        Runs in a background thread. The callback `audio_callback` is invoked by sounddevice
        on its own thread. When a stable pitch is found, it emits note_detected signal.
        """
        def audio_callback(indata, frames, time_info, status):
            if status:
                # You can print or log `status` if desired
                pass

            signal = indata[:, 0]
            # Silence threshold: skip if too quiet
            if np.max(np.abs(signal)) < 0.005:
                return

            # Ask NoteFinder to analyze
            self.noteTool.getNote(44100, signal)
            current_note = self.noteTool.currentNote + str(self.noteTool.currentOrdre)

            if current_note == self.lastStableNote:
                self.stabilityCounter += 1
            else:
                self.stabilityCounter = 0
                self.lastStableNote = current_note

            if self.stabilityCounter >= self.requiredStability:
                # Emit on the GUI thread: note name and ecart value
                self.signals.note_detected.emit(current_note, self.noteTool.currentEcart)
                self.stabilityCounter = 0

        try:
            device_index = AudioSettingsManager.get_input_device()
            with sd.InputStream(
                callback=audio_callback,
                channels=1,
                samplerate=44100,
                blocksize=4096,
                device=device_index
            ):
                while self.running:
                    sd.sleep(100)
        except Exception as e:
            print("Microphone error:", e)

    def closeEvent(self, event):
        """
        When the widget closes, signal the thread to stop, then join it.
        """
        self.running = False
        self.audio_thread.join()
        event.accept()
