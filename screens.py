from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton
from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QMovie, QPainter, QPixmap, QFont
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
    # Signal to notify parent when start button is clicked
    start_button_clicked = pyqtSignal()
    
    def __init__(self, number, text=None, color=None):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # Remove margins to not interfere with background
        
        """label = QLabel(text if text else str(number))
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 32px; font-weight: bold;")
        layout.addWidget(label)"""

        # Movie label setup
        self.movie_label = QLabel()
        self.movie_label.setAlignment(Qt.AlignCenter)
        
        self.setLayout(layout)
        movie = QMovie("Assets/BootupLM.gif")
        movie.setScaledSize(QSize(1024, 600))
        self.movie_label.setMovie(movie)
        layout.addWidget(self.movie_label)
        movie.start()

        # Add Start button only for the home screen (number 0)
        if number == 0:
            self.start_button = QPushButton("START", self)
            self.start_button.setFixedSize(180, 60)
            self.start_button.setStyleSheet("""
                QPushButton {
                    background-color: rgba(76, 175, 80, 0.9);
                    color: white;
                    border: 2px solid rgba(255, 255, 255, 0.3);
                    border-radius: 30px;
                    font-size: 22px;
                    font-weight: bold;
                    font-family: Arial, sans-serif;
                }
                QPushButton:hover {
                    background-color: rgba(69, 160, 73, 0.95);
                    border: 2px solid rgba(255, 255, 255, 0.5);
                    transform: scale(1.05);
                }
                QPushButton:pressed {
                    background-color: rgba(61, 139, 64, 1.0);
                    border: 2px solid rgba(255, 255, 255, 0.7);
                }
            """)
            self.start_button.clicked.connect(self.on_start_clicked)
            # Position the button absolutely to not interfere with the layout
            self.start_button.hide()  # Initially hidden, will be shown after resize

        if color:
            self.setStyleSheet(f"background-color: {color};")
    
    def resizeEvent(self, event):
        """Position the start button when the widget is resized"""
        super().resizeEvent(event)
        if hasattr(self, 'start_button'):
            # Position the button at the bottom center of the screen
            button_x = (self.width() - self.start_button.width()) // 2
            button_y = self.height() - self.start_button.height() - 50  # 50px from bottom
            self.start_button.move(button_x, button_y)
            self.start_button.show()
            self.start_button.raise_()  # Ensure button is on top
    
    def on_start_clicked(self):
        """Emit signal when start button is clicked"""
        self.start_button_clicked.emit()
