from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QComboBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPen, QBrush, QPainter, QColor, QFont
import sounddevice as sd
import numpy as np
import threading
from Modules.tuner.TunerObject import NoteFinder
from Modules.Parametres.logic import load_background, draw_background

class renderArea(QWidget):
    def __init__(self):
        super().__init__()

        self.noteTool = NoteFinder()
        self.noteHeard = False

        # --- Label Note ---
        font = QFont("Arial", 60, QFont.Bold, italic=False)
        self.LabelNote = QLabel(text="A4")
        self.LabelNote.setFont(font)
        self.LabelNote.setAlignment(Qt.AlignCenter)
        self.LabelNote.setStyleSheet("color: #2C3E50;")

        # --- Dropdown for Microphone Selection ---
        self.device_selector = QComboBox()
        self.device_selector.addItems([f"{i}: {name}" for i, name in self.list_input_devices()])
        self.device_selector.setStyleSheet("""
            QComboBox {
                font-size: 18px;
                padding: 10px 20px;
                background-color: #5d8271;
                color: white;
                border: none;
                border-radius: 8px;
            }
            QComboBox:hover {
                background-color: #4a6b5c;
            }
            QComboBox::drop-down {
                border: none;
            }
        """)
        self.device_selector.setMaximumWidth(300)  # Set maximum width for the dropdown menu
        self.device_selector.currentIndexChanged.connect(self.change_microphone)

        # --- Layout ---
        self.Layout = QVBoxLayout()
        self.Layout.setContentsMargins(40, 30, 40, 30)
        self.Layout.setSpacing(20)

        self.Layout.addWidget(self.device_selector, alignment=Qt.AlignCenter)
        self.Layout.addSpacing(20)
        self.Layout.addWidget(self.LabelNote)
        self.Layout.addStretch(1)

        self.image = load_background()
        self.setLayout(self.Layout)

        # Variables de stabilité
        self.lastStableNote = ""
        self.stabilityCounter = 0
        self.requiredStability = 3  # Plus c'est grand, plus c'est stable

        # Initialisation des variables audio
        self.running = True
        self.selected_device = 0  # Par défaut, le premier périphérique
        self.audio_thread = threading.Thread(target=self.listen_micro, daemon=True)
        self.audio_thread.start()

    def list_input_devices(self):
        """Liste les périphériques d'entrée disponibles."""
        devices = sd.query_devices()
        input_devices = [
            (i, dev['name']) for i, dev in enumerate(devices) if dev['max_input_channels'] > 0
        ]
        return input_devices

    def change_microphone(self, index):
        """Change le périphérique d'entrée sélectionné."""
        self.selected_device = int(self.device_selector.currentText().split(":")[0])
        print(f"Microphone sélectionné : {self.selected_device}")
        self.restart_listening()

    def restart_listening(self):
        """Redémarre l'écoute avec le nouveau périphérique sélectionné."""
        self.running = False
        if self.audio_thread and self.audio_thread.is_alive():
            self.audio_thread.join()

        self.running = True
        self.audio_thread = threading.Thread(target=self.listen_micro, daemon=True)
        self.audio_thread.start()

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
            # Vérifiez si le périphérique prend en charge le taux d'échantillonnage
            sd.check_input_settings(device=self.selected_device, samplerate=44100)

            with sd.InputStream(callback=callback, channels=1, samplerate=44100, blocksize=4096, device=(self.selected_device, None)):
                while self.running:
                    sd.sleep(100)
        except sd.PortAudioError as e:
            print(f"Erreur micro : {e}")
        except Exception as e:
            print(f"Erreur inattendue : {e}")

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

    def closeEvent(self, event):
        self.running = False
        if self.audio_thread:
            self.audio_thread.join()
        event.accept()