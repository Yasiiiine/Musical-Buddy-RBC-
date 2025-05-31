from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QMovie, QPainter, QPixmap
import config
from core.utils import asset_path

class TransitionScreen(QWidget):
    def __init__(self):
        super().__init__()
        
        self.image_label = QLabel(self)
        self.set_background()
        self.image_label.setScaledContents(True)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setAttribute(Qt.WA_TransparentForMouseEvents)

        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("background-color: black;")  # Optional: or transparent

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.image_label.setGeometry(self.rect())  # Centered and scaled with window
    
    def set_background(self):
        """
        Switches image_label’s pixmap to light or dark,
        based on config.is_dark_mode.
        """
        if config.is_dark_mode:
            chosen = config.bg_dark_image
        else:
            chosen = config.bg_light_image

        pix = QPixmap(asset_path(chosen))
        self.image_label.setPixmap(pix)
        # Ensure it always fills the widget’s rect (resizeEvent handles geometry)
        self.image_label.setGeometry(self.rect())

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
