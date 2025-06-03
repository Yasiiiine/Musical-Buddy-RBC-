from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QProgressBar, QSizePolicy, QHBoxLayout, QScrollArea
from PyQt5.QtCore import Qt, QTimer, QEvent, pyqtSlot
import os
from Modules.player.logic import AudioPlayer
from core.styles import retro_label_font, bpm_label_style

class Module4Screen(QWidget):
    def __init__(self):
        super().__init__()

        self.recording_buttons = []
        self.selected_index = 0
        self.visible_range_start = 0
        self.items_per_page = 3

        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.recordings_dir = os.path.join(base_dir, '..', '..', 'recordings')
        self.recordings = [f for f in os.listdir(self.recordings_dir) if f.endswith('.wav')]
        self.recordings.sort()  # Sort initially for consistent order

        self.player = AudioPlayer(self.recordings_dir)

        self.label = QLabel("Select a recording to play:")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFont(retro_label_font(32))
        self.label.setStyleSheet(bpm_label_style())

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedWidth(500)
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

        layout = QVBoxLayout()
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(20)
        layout.addWidget(self.label)

        progress_bar_container = QWidget()
        progress_bar_layout = QHBoxLayout()
        progress_bar_layout.setContentsMargins(0, 0, 0, 0)
        progress_bar_layout.addStretch()
        progress_bar_layout.addWidget(self.progress_bar)
        progress_bar_layout.addStretch()
        progress_bar_container.setLayout(progress_bar_layout)
        layout.addWidget(progress_bar_container)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.3);
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                background: none;
                height: 0px;
            }
        """)

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        self.recording_buttons_layout = QVBoxLayout()
        self.recording_buttons_layout.setSpacing(10)
        scroll_content.setLayout(self.recording_buttons_layout)

        scroll_area.setWidget(scroll_content)
        scroll_area.setFixedHeight(self.items_per_page * 50 + 10)
        scroll_area.setFixedWidth(550)
        layout.addWidget(scroll_area, alignment=Qt.AlignHCenter)

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

    def shorten_text(self, text, max_length=40):
        if len(text) <= max_length:
            return text
        else:
            return text[:max_length-3] + "..."

    def update_recording_buttons(self):
        for i in reversed(range(self.recording_buttons_layout.count())):
            widget = self.recording_buttons_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        for i in range(len(self.recordings)):
            button = QPushButton(self.recordings[i])
            button.setFixedWidth(500)
            button.setMinimumHeight(30)
            button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

            button.clicked.connect(lambda checked, r=self.recordings[i]: self.play_recording(r))
            button.installEventFilter(self)

            if i == self.selected_index:
                button.setStyleSheet("""
                    QPushButton {
                        font-size: 14px;
                        padding: 4px 10px;
                        background-color: #555555;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        text-align: left;
                    }
                """)
            else:
                button.setStyleSheet("""
                    QPushButton {
                        font-size: 14px;
                        padding: 4px 10px;
                        background-color: #5d8271;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        text-align: left;
                    }
                """)

            container = QWidget()
            container_layout = QHBoxLayout()
            container_layout.setContentsMargins(0, 0, 0, 0)
            container_layout.addStretch()
            container_layout.addWidget(button)
            container_layout.addStretch()
            container.setLayout(container_layout)

            self.recording_buttons_layout.addWidget(container)

    def eventFilter(self, source, event):
        if event.type() == QEvent.Enter and isinstance(source, QPushButton):
            for i in range(self.recording_buttons_layout.count()):
                container = self.recording_buttons_layout.itemAt(i).widget()
                if container:
                    button = container.layout().itemAt(1).widget()
                    if button == source:
                        if self.selected_index != i:
                            prev_container = self.recording_buttons_layout.itemAt(self.selected_index).widget()
                            prev_button = prev_container.layout().itemAt(1).widget()
                            prev_button.setStyleSheet("""
                                QPushButton {
                                    font-size: 14px;
                                    padding: 4px 10px;
                                    background-color: #5d8271;
                                    color: white;
                                    border: none;
                                    border-radius: 6px;
                                    text-align: left;
                                }
                            """)
                            button.setStyleSheet("""
                                QPushButton {
                                    font-size: 14px;
                                    padding: 4px 10px;
                                    background-color: #555555;
                                    color: white;
                                    border: none;
                                    border-radius: 6px;
                                    text-align: left;
                                }
                            """)
                            self.selected_index = i
                        break
        return super().eventFilter(source, event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Up:
            if self.selected_index > 0:
                self.selected_index -= 1
                self.update_recording_buttons()
        elif event.key() == Qt.Key_Down:
            if self.selected_index < len(self.recordings) - 1:
                self.selected_index += 1
                self.update_recording_buttons()
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if 0 <= self.selected_index < len(self.recordings):
                self.play_recording(self.recordings[self.selected_index])
        else:
            super().keyPressEvent(event)

    def play_recording(self, recording):
        self.player.play(recording)
        display_name = self.shorten_text(recording, max_length=40)
        self.label.setText(f"Playing: {display_name}")
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
            current_val = self.progress_bar.value()
            progress = int((current_val * duration / 100) + 1000)
            percentage = int(progress / duration * 100)
            self.progress_bar.setValue(min(percentage, 100))
        if self.progress_bar.value() >= 100:
            self.timer.stop()
            self.label.setText("Playback finished")

    @pyqtSlot(str)
    def add_new_recording(self, filename):
        """Handle new recording saved by MicRecorder or ADCRecorder."""
        if filename not in self.recordings:
            self.recordings.append(filename)
            self.recordings.sort()  # Maintain sorted order
            self.selected_index = self.recordings.index(filename)  # Select new recording
            self.update_recording_buttons()