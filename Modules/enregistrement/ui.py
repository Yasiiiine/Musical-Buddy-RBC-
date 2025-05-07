from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from Modules.enregistrement.logic import Recorder
from Modules.Parametres.logic import load_background

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
