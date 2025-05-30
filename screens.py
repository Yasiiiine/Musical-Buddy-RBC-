from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QMovie, QPainter, QPixmap
from core.theme_manager import ThemeManager
from config import theme_manager

class TransitionScreen(QWidget):
    def __init__(self):
        super().__init__()
        
        self.image_label = QLabel(self)
        self.image_label.setPixmap(QPixmap(theme_manager.get_background_path()))
        self.image_label.setScaledContents(True)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setAttribute(Qt.WA_TransparentForMouseEvents)

        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("background-color: black;")  # Optional: or transparent

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.image_label.setGeometry(self.rect())  # Centered and scaled with window
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
        movie.setScaledSize(QSize(1024, 600))
        MovieLabel.setMovie(movie)
        layout.addWidget(MovieLabel)
        movie.start()

        
        if color:
            self.setStyleSheet(f"background-color: {color};")
