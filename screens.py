from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
import config
class Screen(QWidget):
    def __init__(self, number):
        super().__init__()

        layout = QVBoxLayout()
        label = QLabel(number)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 50px; font-weight: bold;")

        bg_color = config.BG_COLORS[int(number)]  # Associer couleur à l'écran
        self.setStyleSheet(f"background-color: {bg_color};")

        layout.addWidget(label)
        self.setLayout(layout)
