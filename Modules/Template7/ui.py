# ui.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QProgressBar, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer
from Modules.Template4.logic import AudioPlayer
import Modules.Template4.config as cfg
import os

class Module7Screen(QWidget):
    def __init__(self):
        super().__init__()

        base_dir = os.path.dirname(os.path.abspath(__file__))  # Répertoire du fichier actuel
        self.recordings_dir = os.path.join(base_dir, '..', '..', 'Assets', 'recordings')
        self.recordings = [f for f in os.listdir(self.recordings_dir) if f.endswith('.wav')]

        self.current_page = 0
        self.items_per_page = 3

        self.player = AudioPlayer(self.recordings_dir)
        self.label = QLabel("Select a recording to play:")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("font-size: 24px; font-weight: bold;")

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
                animation: progress-animation 1s ease-in-out infinite;
            }
        """)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.progress_bar)

        # Create layout for recording buttons
        self.recording_buttons_layout = QVBoxLayout()
        layout.addLayout(self.recording_buttons_layout)

        # Add control buttons
        control_layout = QHBoxLayout()
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_playback)
        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self.pause_playback)
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_playback)

        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.pause_button)
        control_layout.addWidget(self.stop_button)
        layout.addLayout(control_layout)

        self.setLayout(layout)
        self.setStyleSheet(f"background-color: {cfg.MODULE_COLOR};")

        self.setFocusPolicy(Qt.StrongFocus)  # Permet de capturer les événements clavier
        self.setFocus()  # Donne le focus au widget

        self.update_recording_buttons()

    def update_recording_buttons(self):
        # Clear existing buttons
        for i in reversed(range(self.recording_buttons_layout.count())):
            self.recording_buttons_layout.itemAt(i).widget().deleteLater()

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
        self.timer.start(1000)  # Update progress every second

    def start_playback(self):
        if self.player.is_paused():
            self.player.resume()
            self.label.setText("Resumed playback")
            self.timer.start(1000)

    def pause_playback(self):
        if self.player.is_playing():
            self.player.pause()
            self.label.setText("Paused playback")
            self.timer.stop()

    def stop_playback(self):
        if self.player.is_playing() or self.player.is_paused():
            self.player.stop()
            self.label.setText("Stopped playback")
            self.progress_bar.setValue(0)
            self.timer.stop()

    def update_progress(self):
        duration = self.player.get_duration()
        current_time = self.player.get_time()
        if duration > 0:
            progress = int((current_time / duration) * 100)
            self.progress_bar.setValue(progress)
        if current_time >= duration:
            self.timer.stop()
            self.label.setText("Playback finished")
        else:
            self.animate_progress_bar()

    def animate_progress_bar(self):
        # Optional: Add logic for smooth animation if needed
        pass

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
            super().keyPressEvent(event)  # Appelle la méthode parente pour d'autres touches