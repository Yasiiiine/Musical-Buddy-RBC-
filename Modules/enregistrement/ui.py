from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPainter, QPixmap
from Modules.enregistrement.logic import Recorder
from AudioSettingsManager import AudioSettingsManager
import Modules.enregistrement.config as cfg
from core.styles import retro_label_font, bpm_label_style
from core.theme_manager import ThemeManager


class Record(QWidget):
    def __init__(self):
        super().__init__()

        self.recorder = Recorder()

        # --- Label Setup ---
        self.label = QLabel("Press E to record")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(retro_label_font(30))
        self.label.setStyleSheet(bpm_label_style())

        # --- Layout ---
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 50, 0, 0)
        self.layout.addWidget(self.label, alignment=Qt.AlignBaseline)
        self.setLayout(self.layout)

        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

        # --- Timer for image updates ---
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(50)  # 20 FPS

    def paintEvent(self, event):
        painter = QPainter(self)

        numRecord = 0
        while numRecord != 6 and self.recorder.soundlevel >= cfg.PLAGES_NIVEAU_SONORE[numRecord]:
            numRecord += 1
        numRecord = max(0, numRecord - 1)

        image_path = f"Assets/record{numRecord}.png"
        pixmap = QPixmap(image_path)

        if not pixmap.isNull():
            target_width = self.width() // 5
            scaled_pixmap = pixmap.scaled(target_width, target_width, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            x_offset = (self.width() - scaled_pixmap.width()) // 2
            y_offset = self.height() // 4 - 10
            painter.drawPixmap(x_offset, y_offset, scaled_pixmap)
        else:
            print(f"Image not found: {image_path}")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_E:
            self.recorder.toggle_recording()

            if self.recorder.short_recording:
                self.label.setText("Too Short!!!!")
                self.recorder.short_recording = False
            elif self.recorder.recording:
                self.label.setText("Press E to stop recording")
            else:
                self.label.setText("Saved! Press E to record again")

            self.setFocus()
        else:
            super().keyPressEvent(event)
