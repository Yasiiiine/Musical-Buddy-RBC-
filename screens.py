from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

class Screen(QWidget):
    def __init__(self, number, text=None, color=None):
        super().__init__()
        layout = QVBoxLayout()
        label = QLabel(text if text else str(number))
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 32px; font-weight: bold;")
        layout.addWidget(label)
        image = QPixmap("Assets/autism.jpg")
        image = image.scaledToHeight(320)
        label.setPixmap(image)

        self.setLayout(layout)
        if color:
            self.setStyleSheet(f"backg++++++round-color: {color};")