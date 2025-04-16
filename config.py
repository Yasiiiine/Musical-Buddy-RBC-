from PyQt5.QtGui import QPainter
from Modules.Parametres.logic import draw_background

WINDOW_WIDTH = 480
WINDOW_HEIGHT = 320
WINDOW_TITLE = "Musical Buddy"
BG = "Assets/BGLM.png"
bootup = "Assets/Bootup.wav"

def paintEvent(self, event):
    """Draw the background image."""
    super().paintEvent(event)
    painter = QPainter(self)
    draw_background(self, painter, self.image)