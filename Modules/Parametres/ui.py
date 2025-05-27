from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QComboBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter

from AudioSettingsManager import AudioSettingsManager
from core.styles import retro_label_font, bpm_label_style
import Modules.Parametres.config as cfg
import config
from config import theme_manager
from core.theme_manager import ThemeManager


class Module7Screen(QWidget):
    def __init__(self):
        super().__init__()

        # --- Title Label ---
        self.label = QLabel(cfg.MODULE_LABEL)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(retro_label_font(32))
        self.label.setStyleSheet(bpm_label_style())

        # --- Toggle Theme Button ---
        self.toggle_button = QPushButton("Toggle Theme")
        self.toggle_button.clicked.connect(self.toggle_theme)
        self.toggle_button.setFixedWidth(200)
        self.toggle_button.setStyleSheet("""
            QPushButton {
                background-color: #5d8271;
                color: white;
                font-size: 18px;
                padding: 10px;
                border: none;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #4a6b5c;
            }
        """)

        # --- Audio Input ComboBox ---
        self.input_selector = QComboBox()
        self.input_selector.addItems(AudioSettingsManager.list_input_devices())
        current_index = AudioSettingsManager.get_input_device()
        if current_index is not None:
            self.input_selector.setCurrentIndex(current_index)
        self.input_selector.currentIndexChanged.connect(
            lambda i: AudioSettingsManager.set_input_device(i)
        )
        self.input_selector.setFixedWidth(300)
        self.input_selector.setStyleSheet("""
            QComboBox {
                font-size: 16px;
                padding: 8px 12px;
                border: 1px solid #aaa;
                border-radius: 8px;
                background-color: #f0f0f0;
            }
            QComboBox QAbstractItemView {
                selection-background-color: #5d8271;
            }
        """)

        # --- Layout ---
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)
        layout.addWidget(self.label, alignment=Qt.AlignCenter)
        layout.addWidget(self.input_selector, alignment=Qt.AlignCenter)
        layout.addWidget(self.toggle_button, alignment=Qt.AlignCenter)
        self.setLayout(layout)

        # --- Theme change listener ---
        theme_manager.theme_changed.connect(self.update_background)

        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

    def toggle_theme(self):
        theme_manager.toggle_theme()

    def update_background(self):
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
