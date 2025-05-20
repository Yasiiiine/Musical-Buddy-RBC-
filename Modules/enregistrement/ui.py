from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont,QPainter, QPixmap
from Modules.enregistrement.logic import Recorder
from Modules.Parametres.logic import load_background
import Modules.enregistrement.config as cfg

class Module3Screen(QWidget):
    def __init__(self):
        super().__init__()

        self.recorder = Recorder()

        # --- Font Setup ---
        font = QFont("Arial", 15, QFont.Bold, italic=False)

        # --- Label Setup ---
        self.label = QLabel("Press E to record")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(font)
        self.label.setStyleSheet("color: #2C3E50;")

        # --- Layout ---
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 50, 0, 0)  # Add a top margin of 50px
        self.layout.addWidget(self.label, alignment=Qt.AlignBaseline)
        self.setLayout(self.layout)

        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

        # Timer to update the UI
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(50)  # Update every 50ms

    def paintEvent(self, event):
        painter = QPainter(self)

        # Determine which image to display based on the sound level
        numRecord = 0
        while numRecord != 6 and self.recorder.soundlevel >= cfg.PLAGES_NIVEAU_SONORE[numRecord]:
            numRecord += 1
        numRecord = max(0, numRecord - 1)  # Ensure numRecord is within valid range

        # Load the corresponding image
        image_path = f"Assets/record{numRecord}.png"
        pixmap = QPixmap(image_path)

        if not pixmap.isNull():
            # Scale the image to a smaller size (e.g., 20% of the widget's width)
            target_width = self.width() // 5
            scaled_pixmap = pixmap.scaled(target_width, target_width, Qt.KeepAspectRatio, Qt.SmoothTransformation)

            # Center the image horizontally and position it lower overall
            x_offset = (self.width() - scaled_pixmap.width()) // 2
            y_offset = self.height() // 4 - 10  # Lower the icon to the upper quarter of the widget
            painter.drawPixmap(x_offset, y_offset, scaled_pixmap)
        else:
            print(f"Image not found: {image_path}")  # Debugging

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
            self.setFocus()  # Ensure the widget regains focus after recording
        else:
            super().keyPressEvent(event)