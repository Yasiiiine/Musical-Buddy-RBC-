from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter
from Modules.Parametres.logic import load_background, draw_background  # or wherever you defined it

class TransitionScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.bg = load_background()

    def paintEvent(self, event):
        painter = QPainter(self)
        draw_background(self, painter, self.bg)
class Screen(QWidget):
    def __init__(self, number, text=None, color=None):
        super().__init__()
        layout = QVBoxLayout()
        
        """label = QLabel(text if text else str(number))
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 32px; font-weight: bold;")
        layout.addWidget(label)"""

        # Movie label setup
        MovieLabel = QLabel()
        MovieLabel.setAlignment(Qt.AlignCenter)
        
        self.setLayout(layout)
        movie = QMovie("Assets/BootupLM.gif")
        movie.setScaledSize(QSize(480, 320))
        MovieLabel.setMovie(movie)
        layout.addWidget(MovieLabel)
        movie.start()

        
        if color:
            self.setStyleSheet(f"background-color: {color};")
