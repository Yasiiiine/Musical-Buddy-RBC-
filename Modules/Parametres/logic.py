from PyQt5.QtGui import QPixmap, QPainter, QPaintEvent
from PyQt5.QtCore import Qt
import Modules.Parametres.config as cfg
import config as cg
import os

def load_background():
    theme = cg.theme
    image_name = 'background_LM.png' if theme == 'light' else 'background_DM.png'
    image_path = os.path.join('Assets', image_name)
    return QPixmap(image_path)

def draw_background(widget, painter, pixmap):
    """Draws a scaled background image on the given widget."""
    if not pixmap.isNull():
        scaled = pixmap.scaled(widget.size(),
                               Qt.KeepAspectRatioByExpanding,
                               Qt.SmoothTransformation)
        painter.drawPixmap(0, 0, scaled)


