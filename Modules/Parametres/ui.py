from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QComboBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter

from AudioSettingsManager import AudioSettingsManager
from core.styles import retro_label_font, bpm_label_style
import Modules.Parametres.config as cfg
import config
from core.audio_utils import initialize_audio_devices


class Module7Screen(QWidget):
    def __init__(self):
        super().__init__()

        # --- Title Label ---
        self.label = QLabel(cfg.MODULE_LABEL)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(retro_label_font(32))
        self.label.setStyleSheet(bpm_label_style())

        # --- Audio Output ComboBox ---
        self.output_selector = QComboBox()
        self.output_selector.addItems(AudioSettingsManager.list_output_devices())
        current_out = AudioSettingsManager.get_output_device()
        if current_out is not None:
            self.output_selector.setCurrentIndex(current_out)
        self.output_selector.currentIndexChanged.connect(self.on_output_changed)
        self.output_selector.setFixedWidth(300)
        self.output_selector.setStyleSheet(
            """
            QComboBox {
                font-size: 16px;
                padding: 8px 12px;
                border: 1px solid #aaa;
                border-radius: 8px;
            }
            QComboBox::drop-down {
                border: none;
            }
            """
        )

        # --- Toggle Theme Button ---
        self.toggle_button = QPushButton("Toggle Theme")
        self.toggle_button.clicked.connect(self.toggle_dark_mode)
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

        # --- Audio Input ComboBox (EXISTING) ---
        self.input_selector = QComboBox()
        # Populate with all available input devices
        self.input_selector.addItems(AudioSettingsManager.list_input_devices())
        # If the user had previously chosen one, set it as current
        current_index = AudioSettingsManager.get_input_device()
        if current_index is not None:
            self.input_selector.setCurrentIndex(current_index)
        # When the user picks a different device, store it
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
            }
            QComboBox::drop-down {
                border: none;
            }
        """)
        

        # --- Layout Setup ---
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)

        layout.addWidget(self.label, alignment=Qt.AlignCenter)
        layout.addWidget(self.input_selector, alignment=Qt.AlignCenter)
        layout.addWidget(self.output_selector, alignment=Qt.AlignCenter)  # <- new line
        layout.addWidget(self.toggle_button, alignment=Qt.AlignCenter)

        self.setLayout(layout)
    
    def toggle_dark_mode(self):
        """
        Flip the global config.is_dark_mode boolean, then ask
        the MainWindow to re-draw its background for all modules.
        """
        # 1) Flip the flag
        config.is_dark_mode = not config.is_dark_mode

        # 2) Tell MainWindow to update its background immediately.
        #    `self.window()` returns the top-level QMainWindow (MainWindow).
        mw = self.window()
        if hasattr(mw, "set_background"):
            mw.set_background()

        for widget in mw.findChildren(QLabel):
            # re‐apply style if we know this label should use bpm_label_style
            widget.setStyleSheet(bpm_label_style())

    
    def on_output_changed(self, index):
        # 1) Store it in AudioSettingsManager
        AudioSettingsManager.set_output_device(index)
        # 2) Immediately reapply to SoundDevice
        initialize_audio_devices()

    def update_background(self):
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        # (existing painting code if any…)
