from PyQt5.QtGui import QPixmap, QPainter, QPaintEvent
from PyQt5.QtCore import Qt
import Modules.Parametres.config as cfg
import config as cg

def load_background():
    return QPixmap(cg.BG)

def draw_background(widget, painter, pixmap):
    """Draws a scaled background image on the given widget."""
    if not pixmap.isNull():
        scaled = pixmap.scaled(widget.size(),
                               Qt.KeepAspectRatioByExpanding,
                               Qt.SmoothTransformation)
        painter.drawPixmap(0, 0, scaled)


