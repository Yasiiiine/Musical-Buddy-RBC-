from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QProgressBar, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QPainter
from Modules.Template4.logic import AudioPlayer
import Modules.Template4.config as cfg
import config
import os
from Modules.Parametres.logic import load_background, draw_background


class Module4Screen(QWidget):
    def __init__(self):
        super().__init__()

        # Load background image
        self.image = load_background()

        # Directory setup
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.recordings_dir = os.path.join(base_dir, '..', '..', 'Assets', 'recordings')
        self.recordings = [f for f in os.listdir(self.recordings_dir) if f.endswith('.wav')]

        self.current_page = 0
        self.items_per_page = 3

        # Audio player setup
        self.player = AudioPlayer(self.recordings_dir)

        # UI Elements
        self.label = QLabel("Select a recording to play:")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 24px; font-weight: bold; color: white;")

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #555;
                border-radius: 5px;
                background-color: #f3f3f3;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #4caf50;
                border-radius: 5px;
            }
        """)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)

        # Main layout
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.progress_bar)

        # Recording buttons layout
        self.recording_buttons_layout = QVBoxLayout()
        layout.addLayout(self.recording_buttons_layout)

        # Playback control buttons
        control_layout = QHBoxLayout()
        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")

        self.start_button.clicked.connect(self.start_playback)
        self.stop_button.clicked.connect(self.stop_playback)

        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.stop_button)
        layout.addLayout(control_layout)

        self.setLayout(layout)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

        self.update_recording_buttons()

    def update_recording_buttons(self):
        # Clear existing buttons
        for i in reversed(range(self.recording_buttons_layout.count())):
            widget = self.recording_buttons_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Add buttons for the current page
        start_index = self.current_page * self.items_per_page
        end_index = min(start_index + self.items_per_page, len(self.recordings))
        for recording in self.recordings[start_index:end_index]:
            button = QPushButton(recording)
            button.clicked.connect(lambda checked, r=recording: self.play_recording(r))
            self.recording_buttons_layout.addWidget(button)

    def play_recording(self, recording):
        self.player.play(recording)
        self.label.setText(f"Playing: {recording}")
        self.progress_bar.setValue(0)
        self.timer.start(1000)

    def start_playback(self):
        print("Start functionality is handled by play_recording.")

    def stop_playback(self):
        if self.player.is_playing():
            self.player.stop()
            self.label.setText("Stopped playback")
            self.progress_bar.setValue(0)
            self.timer.stop()

    def update_progress(self):
        duration = self.player.get_duration()
        if duration > 0:
            progress = int((self.progress_bar.value() + 1000) / duration * 100)
            self.progress_bar.setValue(progress)
        if self.progress_bar.value() >= 100:
            self.timer.stop()
            self.label.setText("Playback finished")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Up:
            if self.current_page > 0:
                self.current_page -= 1
                self.update_recording_buttons()
                self.label.setText(f"Page {self.current_page + 1}")
        elif event.key() == Qt.Key_Down:
            if (self.current_page + 1) * self.items_per_page < len(self.recordings):
                self.current_page += 1
                self.update_recording_buttons()
                self.label.setText(f"Page {self.current_page + 1}")
        else:
            super().keyPressEvent(event)