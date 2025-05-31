from PyQt5.QtGui import QFont
import config

def retro_label_font(size=16):
    font = QFont("Arial", 16, QFont.Bold)
    font.setPixelSize(size)
    return font

def bpm_label_style():
    if config.is_dark_mode:
        # Slightly creamy white for dark backgrounds
        text_color = "#F0EDE5"
    else:
        # Original dark blue for light backgrounds
        text_color = "#2C3E50"

    return f"font-weight: bold; color: {text_color}; padding-bottom: 10px; padding-top: 10px;"
