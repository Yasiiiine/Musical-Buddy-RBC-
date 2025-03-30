from TunerObject import NoteFinder
from PyQt5.QtWidgets import QLabel,QVBoxLayout,QWidget
from PyQt5.QtGui import QPixmap,QPen,QBrush,QPaintEvent, QPainter,QColor



class renderArea(QWidget):
    def __init__(self, parentWidget, pixMap):
        super().__init__()
        self.pixMap = QPixmap()
        
        #self.setParent(parentWidget)
        self.noteTool = NoteFinder()

        self.Label = QLabel(text=" ")
        layout = QVBoxLayout()
        layout.addWidget(self.Label)
        self.setLayout(layout)


    def paintEvent(self,event):
        painter = QPainter(self)

        pen = QPen()
        pen.setWidth(5.0)
        painter.setPen(pen)

        brush = painter.brush()
        brush.setColor(QColor.fromRgb(255,123,0))
        painter.setBrush(brush)

        rect = self.parent.rect()
        rect.x -= 20
        rect.y -= 20

        if abs(self.noteTool.currentEcart - round(self.noteTool.currentEcart)) < 0.1:
            
            brush.setColor(QColor.fromRgb(0,255,0))
            painter.fillRect(rect)

        else:

            brush.setColor(QColor.fromRgb(255,123,0))
            painter.fillRect(rect)


        
