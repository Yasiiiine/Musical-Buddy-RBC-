# ui.py
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap,QPen,QBrush,QPaintEvent, QPainter, QColor, QFont
from PyQt5.QtMultimedia import QAudioRecorder, QAudioProbe, QAudioInput
import Modules.tuner.config as cfg
from Modules.tuner.TunerObject import NoteFinder
from Modules.Parametres.logic import load_background, draw_background
import config


from numpy.random import random

class renderArea(QWidget):
    def __init__(self):
        super().__init__()
        
        self.noteTool = NoteFinder()
        self.noteHeard = False
        
        font = QFont("Arial", 50, weight = 800, italic=True)
        self.LabelNote = QLabel(text= (self.noteTool.currentNote + str(self.noteTool.currentOrdre)))
        self.LabelNote.setFont(font)
        self.LabelNote.setAlignment(Qt.AlignCenter)

        self.Layout = QVBoxLayout()
        self.Layout.addWidget(self.LabelNote)

        self.image = load_background()

        self.setLayout(self.Layout)

        # self.recorder = QAudioRecorder()
        # self.audioInput = QAudioInput()
        # self.recorder.setAudioInput(self.audioInput)
        # self.probe = QAudioProbe()
        # self.probe.setSource(self.recorder)
        # self.probe.audioBufferProbed.connect(self.recorder.processBuffer())
        

    def paintEvent(self,event):
        painter = QPainter(self)


        pen = QPen(Qt.black)
        pen.setStyle(Qt.PenStyle.NoPen)
        painter.setPen(pen)

        brush = QBrush()
        #brush.setStyle(Qt.BrushStyle.SolidPattern)
        painter.setBrush(brush)

        rect = self.size()
        rect.setWidth(rect.width() - 20) 
        rect.setHeight(rect.height() - 20) 

        painter.drawRect(self.x() + 10, self.y() + 10, rect.width(), rect.height())

        if self.noteHeard:
            if abs(self.noteTool.currentEcart - round(self.noteTool.currentEcart)) < 0.1:
                print("Good !")
                brush.setColor(QColor("#00B600"))
                painter.setBrush(brush)
                painter.eraseRect(self.x() + 10, self.y() + 10, rect.width(), rect.height())
                painter.drawRect(self.x() + 10, self.y() + 10, rect.width(), rect.height())

            else:

                brush.setColor(QColor.fromRgb(255,123,0))
                painter.setBrush(brush)
                print("Not good !")
                painter.eraseRect(self.x() + 10, self.y() + 10, rect.width(), rect.height())
                painter.drawRect(self.x() + 10, self.y() + 10, rect.width(), rect.height())
                pen.setWidth(30)
                pen.setColor(Qt.blue)
                pen.setStyle(Qt.PenStyle.SolidLine)
                painter.setPen(pen)
                painter.drawPoint(round(((self.size().width() - 60)*((1/2) + self.noteTool.currentEcart))) + 30,268)

        pen.setColor(Qt.black)
        pen.setStyle(Qt.PenStyle.SolidLine)
        pen.setWidth(10)
        painter.setPen(pen)
        
        painter.drawLine(30,238,30,298)
        painter.drawLine(166,238,166,298)
        painter.drawLine(303,238,303,298)
        painter.drawLine(439,238,439,298)
        painter.drawLine(575,238,575,298)
        
        
        
        self.noteHeard = False

    def mousePressEvent(self, a0):
        self.noteHeard = not self.noteHeard
        self.noteTool.currentEcart = (random()-1/2)
        print(self.noteTool.currentEcart)
        self.LabelNote.setText((self.noteTool.currentNote + str(self.noteTool.currentOrdre)))
        self.repaint()

    def processBuffer():
        pass