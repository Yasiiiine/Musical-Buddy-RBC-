from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QSizePolicy
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPainter, QPixmap
from Modules.enregistrement.logic import Recorder
import Modules.enregistrement.config as cfg
from core.styles import retro_label_font, bpm_label_style


class Record(QWidget):
    def __init__(self):
        super().__init__()

        self.recorder = Recorder()
        self.recorder.recording_too_short.connect(self.on_too_short)

        # --- Label Setup ---
        self.label = QLabel("Press the button to record")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(retro_label_font(26))
        self.label.setStyleSheet(bpm_label_style())

        # --- Button Setup ---
        self.button = QPushButton("Start Recording")
        self.button.setFont(retro_label_font(20))
        self.button.setStyleSheet("padding: 12px; background-color: #403F4C; color: white; border-radius: 10px;")
        self.button.clicked.connect(self.toggle_recording)
        self.button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.button.setCursor(Qt.PointingHandCursor)

        # --- Layout ---
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 40, 0, 0)
        self.layout.setSpacing(5)
        self.layout.addWidget(self.label, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.button, alignment=Qt.AlignCenter)
        self.setLayout(self.layout)

        # --- Timer for visual updates ---
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(50)

    def paintEvent(self, event):
        painter = QPainter(self)

        # Determine volume level
        numRecord = 0
        while numRecord != 6 and self.recorder.soundlevel >= cfg.PLAGES_NIVEAU_SONORE[numRecord]:
            numRecord += 1
        numRecord = max(0, numRecord - 1)

        image_path = f"Assets/record{numRecord}.png"
        pixmap = QPixmap(image_path)

        if not pixmap.isNull():
            # Smaller image size
            target_width = self.width() // 8
            scaled_pixmap = pixmap.scaled(target_width, target_width, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            x_offset = (self.width() - scaled_pixmap.width()) // 2
            y_offset = self.height() // 2  # Lowered to center beneath label & button
            painter.drawPixmap(x_offset, y_offset, scaled_pixmap)
        else:
            print(f"Image not found: {image_path}")

    def toggle_recording(self):
        self.recorder.toggle_recording()

        if self.recorder.recording:
            self.label.setText("Recording... press again to stop")
            self.button.setText("Stop Recording")
        else:
            if not self.recorder.short_recording:
                self.label.setText("Saved! Press to record again")
                self.button.setText("Start Recording")

    def on_too_short(self):
        self.label.setText("Too short!")
        self.button.setText("Try Again")
