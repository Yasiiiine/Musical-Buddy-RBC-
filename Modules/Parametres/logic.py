from PyQt5.QtGui import QPixmap, QPainter, QPaintEvent
from PyQt5.QtCore import Qt
import Modules.Parametres.config as cfg
import config as cg
import os

def load_background():
    """Loads the background image based on the current theme."""
    bg_path = cg.BGList[0] if cg.theme_manager.theme == 'light' else cg.BGList[1]
    pixmap = QPixmap(bg_path)
    if pixmap.isNull():
        raise FileNotFoundError(f"Background image not found: {bg_path}")
    return pixmap

def draw_background(widget, painter, image):
    if not image or image.isNull():
        return

    widget_size = widget.size()
    scaled = image.scaled(widget_size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)

    # Center the image
    x = (widget.width() - scaled.width()) // 2
    y = (widget.height() - scaled.height()) // 2
    painter.drawPixmap(x, y, scaled)
        
def update_background(self):
    self.image = load_background()
    self.update()