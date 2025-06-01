from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QSizePolicy, QMessageBox
from PyQt5.QtCore import Qt, QTimer, pyqtSlot
from PyQt5.QtGui import QPainter, QPixmap, QFont

# Import both Recorder classes
from Modules.enregistrement.logic import MicRecorder, ADCRecorder
import Modules.enregistrement.config as cfg

from core.styles import retro_label_font, bpm_label_style


class Record(QWidget):
    def __init__(self):
        super().__init__()

        # ─── Instantiate both recorders ─────────────────────────────────────────
        self.mic_recorder = MicRecorder()
        self.adc_recorder = ADCRecorder()

        # Connect “too short” signals to separate handlers
        self.mic_recorder.recording_too_short.connect(self.on_mic_too_short)
        self.adc_recorder.recording_too_short.connect(self.on_adc_too_short)

        # ─── Build the UI ────────────────────────────────────────────────────────

        # MIC section
        self.mic_label = QLabel("Microphone Recording")
        self.mic_label.setAlignment(Qt.AlignCenter)
        self.mic_label.setFont(retro_label_font(26))
        self.mic_label.setStyleSheet(bpm_label_style())

        self.btn_record_mic = QPushButton("Start Recording")
        self.btn_record_mic.setFont(retro_label_font(20))
        self.btn_record_mic.setStyleSheet(
            "padding: 12px; background-color: #403F4C; color: white; border-radius: 10px;"
        )
        self.btn_record_mic.clicked.connect(self.on_mic_toggled)
        self.btn_record_mic.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.btn_record_mic.setCursor(Qt.PointingHandCursor)

        # Spacer between sections
        self.spacer = QLabel("")  # empty line for visual separation

        # ADC section
        self.adc_label = QLabel("ADC (MCP3008) Recording")
        self.adc_label.setAlignment(Qt.AlignCenter)
        self.adc_label.setFont(retro_label_font(26))
        self.adc_label.setStyleSheet(bpm_label_style())

        self.btn_record_adc = QPushButton("Start Recording")
        self.btn_record_adc.setFont(retro_label_font(20))
        self.btn_record_adc.setStyleSheet(
            "padding: 12px; background-color: #403F4C; color: white; border-radius: 10px;"
        )
        self.btn_record_adc.clicked.connect(self.on_adc_toggled)
        self.btn_record_adc.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.btn_record_adc.setCursor(Qt.PointingHandCursor)

        # ─── Layout everything vertically ────────────────────────────────────────
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 40, 0, 0)
        self.layout.setSpacing(5)

        # Add MIC widgets
        self.layout.addWidget(self.mic_label, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.btn_record_mic, alignment=Qt.AlignCenter)

        # Add a small blank line
        self.layout.addWidget(self.spacer)

        # Add ADC widgets
        self.layout.addWidget(self.adc_label, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.btn_record_adc, alignment=Qt.AlignCenter)

        self.setLayout(self.layout)

        # ─── Timer for repaints (so the level meters update) ──────────────────
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(50)  # 50 ms tick to trigger paintEvent

    @pyqtSlot()
    def on_mic_toggled(self):
        """
        User clicked the MIC button.
        Toggle mic_recorder and update button text/label.
        """
        if self.mic_recorder.recording:
            # Currently recording → stop
            self.btn_record_mic.setText("Start Recording")
        else:
            # Not recording → start
            self.btn_record_mic.setText("Stop Recording")
            self.mic_label.setText("Recording... press again to stop")

        self.mic_recorder.toggle_recording()

    @pyqtSlot()
    def on_adc_toggled(self):
        """
        User clicked the ADC button.
        Toggle adc_recorder and update button text/label.
        """
        if self.adc_recorder.recording:
            self.btn_record_adc.setText("Start Recording")
        else:
            self.btn_record_adc.setText("Stop Recording")
            self.adc_label.setText("Recording... press again to stop")

        self.adc_recorder.toggle_recording()

    @pyqtSlot()
    def on_mic_too_short(self):
        """
        Called when mic_recorder emits recording_too_short.
        Show a warning and reset the mic label/button.
        """
        QMessageBox.warning(self, "Too short", "Mic recording was too short!")
        self.mic_label.setText("Press the button to record")
        self.btn_record_mic.setText("Start Recording")

    @pyqtSlot()
    def on_adc_too_short(self):
        """
        Called when adc_recorder emits recording_too_short.
        Show a warning and reset the ADC label/button.
        """
        QMessageBox.warning(self, "Too short", "ADC recording was too short!")
        self.adc_label.setText("Press the button to record")
        self.btn_record_adc.setText("Start Recording")

    def paintEvent(self, event):
        """
        Paint two separate level-meter images:
         1) For the mic_recorder, drawn in the upper half.
         2) For the adc_recorder, drawn in the lower half.
        """
        painter = QPainter(self)
        w = self.width()
        h = self.height()

        # ─── Draw MIC level meter ──────────────────────────────────────────────
        # Determine which "recordN.png" to use based on mic_recorder.soundlevel
        numMic = 0
        while numMic != 6 and self.mic_recorder.soundlevel >= cfg.PLAGES_NIVEAU_SONORE[numMic]:
            numMic += 1
        numMic = max(0, numMic - 1)

        mic_image_path = f"Assets/record{numMic}.png"
        mic_pixmap = QPixmap(mic_image_path)
        if not mic_pixmap.isNull():
            # Scale to ~1/8 of width, keep aspect ratio
            target_width = w // 8
            scaled = mic_pixmap.scaled(target_width, target_width, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            x_off = (w - scaled.width()) // 2
            # Place in upper half: center vertically in top half
            y_off = (h // 4) - (scaled.height() // 2)
            painter.drawPixmap(x_off, y_off, scaled)

        # ─── Draw ADC level meter ──────────────────────────────────────────────
        numAdc = 0
        while numAdc != 6 and self.adc_recorder.soundlevel >= cfg.PLAGES_NIVEAU_SONORE[numAdc]:
            numAdc += 1
        numAdc = max(0, numAdc - 1)

        adc_image_path = f"Assets/record{numAdc}.png"
        adc_pixmap = QPixmap(adc_image_path)
        if not adc_pixmap.isNull():
            target_width = w // 8
            scaled = adc_pixmap.scaled(target_width, target_width, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            x_off = (w - scaled.width()) // 2
            # Place in lower half: center vertically in bottom half
            y_off = (3 * h // 4) - (scaled.height() // 2)
            painter.drawPixmap(x_off, y_off, scaled)

        # If images aren’t found, you’ll see a console print (optional)
        # but no exception will be thrown.


# End of ui.py
