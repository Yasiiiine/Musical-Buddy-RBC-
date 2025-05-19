from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont,QPainter
from Modules.enregistrement.logic import Recorder
from Modules.Parametres.logic import load_background
import Modules.enregistrement.config as cfg

class Module3Screen(QWidget):
    def __init__(self):
        super().__init__()

        self.recorder = Recorder()

        font = QFont("Arial", 15, QFont.Bold, italic=False)

        self.label = QLabel("Press E to record")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(font)
        self.label.setStyleSheet("color: #2C3E50;")

        self.image = load_background()

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()
    def paintEvent(self, event):
        painter = QPainter(self)
        # Define which recorder image to show from a table. table in logic or ui ?
        numRecord = 0
        while numRecord != 6 and self.recorder.soundlevel >= cfg.PLAGES_NIVEAU_SONORE[numRecord]:
            numRecord += 1
        numRecord -= 1
        
        # Draw the image inside a specific rectangle
        #  painter.drawImage() 
 
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
