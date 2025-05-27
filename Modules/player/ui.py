from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QProgressBar, QSizePolicy
from PyQt5.QtCore import Qt, QTimer, QEvent
import os
from Modules.player.logic import AudioPlayer
from core.styles import retro_label_font, bpm_label_style
from core.theme_manager import ThemeManager
...




class Module4Screen(QWidget):
    def __init__(self):
        super().__init__()

        self.recording_buttons = []
        self.selected_index = 0
        self.visible_range_start = 0
        self.items_per_page = 3

        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.recordings_dir = os.path.join(base_dir, '..', '..','recordings')
        self.recordings = [f for f in os.listdir(self.recordings_dir) if f.endswith('.wav')]

        self.player = AudioPlayer(self.recordings_dir)

        # Title
        self.label = QLabel("Select a recording to play:")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(retro_label_font(32))
        self.label.setStyleSheet(bpm_label_style())

        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #ddd;
                border: 1px solid #aaa;
                border-radius: 10px;
                height: 18px;
            }
            QProgressBar::chunk {
                background-color: #5d8271;
                border-radius: 10px;
            }
        """)

        # Layouts
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)

        layout.addWidget(self.label)
        layout.addWidget(self.progress_bar)

        self.recording_buttons_layout = QVBoxLayout()
        self.recording_buttons_layout.setSpacing(10)
        layout.addLayout(self.recording_buttons_layout)

        self.stop_button = QPushButton("Stop Playback")
        self.stop_button.clicked.connect(self.stop_playback)
        self.stop_button.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                padding: 10px 20px;
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        layout.addWidget(self.stop_button, alignment=Qt.AlignCenter)

        self.setLayout(layout)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)

        self.update_recording_buttons()

    def update_recording_buttons(self):
        # Clear old buttons
        for i in reversed(range(self.recording_buttons_layout.count())):
            widget = self.recording_buttons_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Show a subset based on the visible window
        end = min(self.visible_range_start + self.items_per_page, len(self.recordings))
        for i in range(self.visible_range_start, end):
            button = QPushButton(self.recordings[i])
            button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

            # Connect the button click to play the recording
            button.clicked.connect(lambda checked, r=self.recordings[i]: self.play_recording(r))

            # Add hover behavior to update selection
            button.installEventFilter(self)

            # Highlight if selected
            if i == self.selected_index:
                button.setStyleSheet("""
                    QPushButton {
                        font-size: 14px;
                        padding: 6px 12px;
                        background-color: #555555;
                        color: white;
                        border: none;
                        border-radius: 6px;
                    }
                """)
            else:
                button.setStyleSheet("""
                    QPushButton {
                        font-size: 14px;
                        padding: 6px 12px;
                        background-color: #5d8271;
                        color: white;
                        border: none;
                        border-radius: 6px;
                    }
                """)
            self.recording_buttons_layout.addWidget(button)

    def eventFilter(self, source, event):
        """Handle hover events to update button selection."""
        if event.type() == QEvent.Enter and isinstance(source, QPushButton):
            # Update the selected index based on the hovered button
            for i in range(self.recording_buttons_layout.count()):
                button = self.recording_buttons_layout.itemAt(i).widget()
                if button == source:
                    # Only update styles if the hovered button is different from the current selection
                    if self.selected_index != self.visible_range_start + i:
                        # Reset the style of the previously selected button
                        prev_button = self.recording_buttons_layout.itemAt(self.selected_index - self.visible_range_start).widget()
                        prev_button.setStyleSheet("""
                            QPushButton {
                                font-size: 14px;
                                padding: 6px 12px;
                                background-color: #5d8271;
                                color: white;
                                border: none;
                                border-radius: 6px;
                            }
                        """)

                        # Update the style of the newly hovered button
                        button.setStyleSheet("""
                            QPushButton {
                                font-size: 14px;
                                padding: 6px 12px;
                                background-color: #555555;
                                color: white;
                                border: none;
                                border-radius: 6px;
                            }
                        """)

                        # Update the selected index
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
                self.play_recording(self.recordings[self.selected_index])
        else:
            super().keyPressEvent(event)

    def play_recording(self, recording):
        self.player.play(recording)
        self.label.setText(f"Playing: {recording}")
        self.progress_bar.setValue(0)
        self.timer.start(1000)

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
