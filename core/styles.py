from PyQt5.QtGui import QFont

def retro_label_font(size=16):
    font = QFont("Arial", 16, QFont.Bold)
    font.setPixelSize(size)
    return font

def bpm_label_style():
    return "font-weight: bold; color: #2C3E50; padding-bottom: 10px; padding-top: 10px;"
