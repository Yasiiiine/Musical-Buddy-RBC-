# ui.py
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QLineEdit, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from Modules.Streamer.logic import MusicPlayer
from core.theme_manager_unused import ThemeManager
from core.styles import retro_label_font, bpm_label_style

class Module6Screen(QWidget):
    def __init__(self):
        super().__init__()

        self.player = MusicPlayer()

        self.label = QLabel("Entrez le nom du morceau et appuyez sur E ou Play")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(retro_label_font(32))
        self.label.setStyleSheet(bpm_label_style())

        self.input = QLineEdit()
        self.input.setPlaceholderText("Nom du morceau ou artiste...")
        self.input.setFont(retro_label_font(20))
        self.input.setAlignment(Qt.AlignCenter)
        self.input.setStyleSheet("""
            QLineEdit {
                background-color: #f0f0f0;
                border: 1px solid #aaa;
                border-radius: 8px;
                padding: 10px 16px;
                font-size: 20px;
                color: #2C3E50;
            }
        """)
        self.input.setFocus()

        self.play_button = QPushButton("Play / Stop")
        self.play_button.setFont(retro_label_font(20))
        self.play_button.setStyleSheet("""
            QPushButton {
                font-size: 20px;
                padding: 10px 24px;
                background-color: #5d8271;
                color: white;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #406356;
            }
        """)
        self.play_button.clicked.connect(self.toggle_play)

        layout = QVBoxLayout()
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)
        layout.addWidget(self.label)
        layout.addWidget(self.input)
        layout.addWidget(self.play_button, alignment=Qt.AlignCenter)
        layout.addStretch(1)
        self.setLayout(layout)

        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

    def toggle_play(self):
        song_name = self.input.text().strip()
        if not self.player.is_playing():
            if song_name:
                self.player.play(song_name)
                self.label.setText(f"Lecture : {song_name} (E ou Play pour stop)")
            else:
                self.label.setText("Veuillez saisir un nom de morceau.")
        else:
            self.player.stop()
            self.label.setText("Entrez le nom du morceau et appuyez sur E ou Play")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_E:
            self.toggle_play()
        else:
            super().keyPressEvent(event)  # allow screen switching with other keys
