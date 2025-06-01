# ui.py
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QMessageBox, QSizePolicy
from PyQt5.QtCore import Qt, QEvent
import os
from core.styles import retro_label_font, bpm_label_style
import Modules.Identifier.config as cfg
from Modules.Identifier.logic import identify_song

class IdentifierScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(f"background-color: {cfg.MODULE_COLOR};")
        self.label = QLabel(cfg.MODULE_LABEL)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(retro_label_font(32))
        self.label.setStyleSheet(bpm_label_style())

        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setWordWrap(True)
        self.result_label.setFont(retro_label_font(18))

        self.selected_index = 0
        self.visible_range_start = 0
        self.items_per_page = 4

        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.recordings_dir = os.path.join(base_dir, '..', '..','recordings')
        self.recordings = [f for f in os.listdir(self.recordings_dir) if f.lower().endswith(('.mp3', '.wav', '.m4a', '.aac', '.flac'))]

        self.recording_buttons_layout = QVBoxLayout()
        self.recording_buttons_layout.setSpacing(10)

        self.update_recording_buttons()

        layout = QVBoxLayout()
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)
        layout.addWidget(self.label)
        layout.addLayout(self.recording_buttons_layout)
        layout.addWidget(self.result_label)
        layout.addStretch(1)
        self.setLayout(layout)

        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

    def update_recording_buttons(self):
        # Clear old buttons
        for i in reversed(range(self.recording_buttons_layout.count())):
            widget = self.recording_buttons_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        end = min(self.visible_range_start + self.items_per_page, len(self.recordings))
        for i in range(self.visible_range_start, end):
            button = QPushButton(self.recordings[i])
            button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
            button.clicked.connect(lambda checked, r=self.recordings[i]: self.identify_recording(r))
            button.installEventFilter(self)
            if i == self.selected_index:
                button.setStyleSheet("""
                    QPushButton {
                        font-size: 16px;
                        padding: 8px 16px;
                        background-color: #555555;
                        color: white;
                        border: none;
                        border-radius: 8px;
                    }
                """)
            else:
                button.setStyleSheet("""
                    QPushButton {
                        font-size: 16px;
                        padding: 8px 16px;
                        background-color: #5d8271;
                        color: white;
                        border: none;
                        border-radius: 8px;
                    }
                """)
            self.recording_buttons_layout.addWidget(button)

    def eventFilter(self, source, event):
        if event.type() == QEvent.Enter and isinstance(source, QPushButton):
            for i in range(self.recording_buttons_layout.count()):
                button = self.recording_buttons_layout.itemAt(i).widget()
                if button == source:
                    if self.selected_index != self.visible_range_start + i:
                        prev_button = self.recording_buttons_layout.itemAt(self.selected_index - self.visible_range_start).widget()
                        prev_button.setStyleSheet("""
                            QPushButton {
                                font-size: 16px;
                                padding: 8px 16px;
                                background-color: #5d8271;
                                color: white;
                                border: none;
                                border-radius: 8px;
                            }
                        """)
                        button.setStyleSheet("""
                            QPushButton {
                                font-size: 16px;
                                padding: 8px 16px;
                                background-color: #555555;
                                color: white;
                                border: none;
                                border-radius: 8px;
                            }
                        """)
                        self.selected_index = self.visible_range_start + i
                    break
        return super().eventFilter(source, event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Up:
            if self.selected_index > 0:
                self.selected_index -= 1
                if self.selected_index < self.visible_range_start:
                    self.visible_range_start -= 1
                self.update_recording_buttons()
        elif event.key() == Qt.Key_Down:
            if self.selected_index < len(self.recordings) - 1:
                self.selected_index += 1
                if self.selected_index >= self.visible_range_start + self.items_per_page:
                    self.visible_range_start += 1
                self.update_recording_buttons()
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if 0 <= self.selected_index < len(self.recordings):
                self.identify_recording(self.recordings[self.selected_index])
        else:
            super().keyPressEvent(event)

    def identify_recording(self, filename):
        file_path = os.path.join(self.recordings_dir, filename)
        self.result_label.setText("Identification en cours...")
        result = identify_song(file_path)
        if 'error' in result:
            QMessageBox.warning(self, "Erreur", result['error'])
            self.result_label.setText("")
        else:
            self.result_label.setText(f"Titre : {result['title']}\nArtiste : {result['artist']}\nAlbum : {result['album']}\nSpotify : {result['spotify_url']}\nApple Music : {result['apple_music_url']}")
