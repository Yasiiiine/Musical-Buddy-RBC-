# Modules/enregistrement/ui.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QSizePolicy, QMessageBox
from PyQt5.QtCore import Qt, QTimer, pyqtSlot
from PyQt5.QtGui import QPainter, QPixmap, QFont

from Modules.enregistrement.logic import MicRecorder, ADCRecorder
import Modules.enregistrement.config as cfg
from core.styles import retro_label_font, bpm_label_style
from Modules.player.ui import Module4Screen

class Record(QWidget):
    def __init__(self, player_widget=None):
        super().__init__()
        self.player_widget = player_widget  # May be a separate instance

        # Instantiate recorders
        self.mic_recorder = MicRecorder()
        self.adc_recorder = ADCRecorder()

        # Connect signals
        self.mic_recorder.recording_too_short.connect(self.on_mic_too_short)
        self.adc_recorder.recording_too_short.connect(self.on_adc_too_short)

        # Defer signal connection to ensure correct player instance
        QTimer.singleShot(0, self.connect_player_signals)

        # MIC section
        self.mic_label = QLabel("Microphone Recording")
        self.mic_label.setAlignment(Qt.AlignCenter)
        self.mic_label.setFont(retro_label_font(18))
        self.mic_label.setStyleSheet(bpm_label_style())

        self.btn_record_mic = QPushButton("Start Recording")
        self.btn_record_mic.setFont(retro_label_font(16))
        self.btn_record_mic.setStyleSheet(
            "padding: 8px; background-color: #403F4C; color: white; border-radius: 8px;"
        )
        self.btn_record_mic.clicked.connect(self.on_mic_toggled)
        self.btn_record_mic.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.btn_record_mic.setCursor(Qt.PointingHandCursor)
        self.btn_record_mic.setFixedSize(150, 40)

        # Separator
        self.separator = QLabel()
        self.separator.setFixedHeight(2)
        self.separator.setStyleSheet("background-color: #888;")

        # ADC section
        self.adc_label = QLabel("ADC (MCP3008) Recording")
        self.adc_label.setAlignment(Qt.AlignCenter)
        self.adc_label.setFont(retro_label_font(18))
        self.adc_label.setStyleSheet(bpm_label_style())

        self.btn_record_adc = QPushButton("Start Recording")
        self.btn_record_adc.setFont(retro_label_font(16))
        self.btn_record_adc.setStyleSheet(
            "padding: 8px; background-color: #403F4C; color: white; border-radius: 8px;"
        )
        self.btn_record_adc.clicked.connect(self.on_adc_toggled)
        self.btn_record_adc.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.btn_record_adc.setCursor(Qt.PointingHandCursor)
        self.btn_record_adc.setFixedSize(150, 40)

        # Disable ADC button on Windows
        if cfg.WINDOWS:
            self.btn_record_adc.setEnabled(False)
            self.btn_record_adc.setText("ADC Unavailable")
            self.adc_label.setText("ADC Recording (Not supported on Windows)")

        # Layout
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 60, 0, 0)  # Keep top margin
        self.layout.setSpacing(1)  # Reduced spacing for tighter layout

        self.layout.addWidget(self.mic_label, alignment=Qt.AlignCenter)
        self.layout.addStretch(1)  # Minimal stretch for image spacing
        self.layout.addWidget(self.btn_record_mic, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.separator, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.adc_label, alignment=Qt.AlignCenter)
        self.layout.addStretch(1)  # Minimal stretch for image spacing
        self.layout.addWidget(self.btn_record_adc, alignment=Qt.AlignCenter)

        self.setLayout(self.layout)

        # Timer for repaints
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(50)

    def connect_player_signals(self):
        """Find the correct Module4Screen instance in MainWindow.screens."""
        parent = self.parent()
        while parent and not hasattr(parent, 'screens'):
            parent = parent.parent()
        if parent and hasattr(parent, 'screens'):
            for screen in parent.screens:
                if isinstance(screen, Module4Screen):
                    self.mic_recorder.recording_saved.connect(screen.add_new_recording)
                    self.adc_recorder.recording_saved.connect(screen.add_new_recording)
                    break
        elif self.player_widget:
            # Fallback to provided player_widget if parent search fails
            self.mic_recorder.recording_saved.connect(self.player_widget.add_new_recording)
            self.adc_recorder.recording_saved.connect(self.player_widget.add_new_recording)

    @pyqtSlot()
    def on_mic_toggled(self):
        """Toggle mic recording and update UI."""
        if self.mic_recorder.recording:
            self.btn_record_mic.setText("Start Recording")
            self.mic_label.setText("Microphone Recording")
        else:
            self.btn_record_mic.setText("Stop Recording")
            self.mic_label.setText("Recording... press again to stop")

        self.mic_recorder.toggle_recording()

    @pyqtSlot()
    def on_adc_toggled(self):
        """Toggle ADC recording and update UI, or show Windows warning."""
        if cfg.WINDOWS:
            QMessageBox.warning(self, "Platform Error", "ADC recording is not supported on Windows.")
            return

        if self.adc_recorder.recording:
            self.btn_record_adc.setText("Start Recording")
            self.adc_label.setText("ADC (MCP3008) Recording")
        else:
            self.btn_record_adc.setText("Stop Recording")
            self.adc_label.setText("Recording... press again to stop")

        self.adc_recorder.toggle_recording()

    @pyqtSlot()
    def on_mic_too_short(self):
        """Handle mic recording too short."""
        QMessageBox.warning(self, "Too short", "Mic recording was too short!")
        self.mic_label.setText("Microphone Recording")
        self.btn_record_mic.setText("Start Recording")

    @pyqtSlot()
    def on_adc_too_short(self):
        """Handle ADC recording too short."""
        if cfg.WINDOWS:
            QMessageBox.warning(self, "Platform Error", "ADC recording is not supported on Windows.")
        else:
            QMessageBox.warning(self, "Too short", "ADC recording was too short!")
        self.adc_label.setText("ADC (MCP3008) Recording")
        self.btn_record_adc.setText("Start Recording")

    def paintEvent(self, event):
        """Paint level meters for mic and ADC."""
        painter = QPainter(self)
        w = self.width()
        h = self.height()

        # MIC level meter (above button)
        numMic = 0
        while numMic != 6 and self.mic_recorder.soundlevel >= cfg.PLAGES_NIVEAU_SONORE[numMic]:
            numMic += 1
        numMic = max(0, numMic - 1)

        mic_image_path = f"Assets/record{numMic}.png"
        mic_pixmap = QPixmap(mic_image_path)
        if not mic_pixmap.isNull():
            target_width = w // 10
            scaled = mic_pixmap.scaled(target_width, target_width, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            x_off = (w - scaled.width()) // 2
            y_off = self.mic_label.y() + self.mic_label.height() + 10  # Below label
            painter.drawPixmap(x_off, y_off, scaled)

        # ADC level meter (above button, only if not Windows)
        if not cfg.WINDOWS:
            numAdc = 0
            while numAdc != 6 and self.adc_recorder.soundlevel >= cfg.PLAGES_NIVEAU_SONORE[numAdc]:
                numAdc += 1
            numAdc = max(0, numAdc - 1)

            adc_image_path = f"Assets/record{numAdc}.png"
            adc_pixmap = QPixmap(adc_image_path)
            if not adc_pixmap.isNull():
                target_width = w // 10
                scaled = adc_pixmap.scaled(target_width, target_width, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                x_off = (w - scaled.width()) // 2
                y_off = self.adc_label.y() + self.adc_label.height() + 10  # Below label
                painter.drawPixmap(x_off, y_off, scaled)