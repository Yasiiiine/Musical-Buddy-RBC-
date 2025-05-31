import os
from PyQt5.QtWidgets import (
    QLabel, QVBoxLayout, QPushButton, QScrollArea, QWidget, QMessageBox
)
from PyQt5.QtCore import Qt
from core.base_screen import BaseScreen
from Modules.transcripteurMIDI.logic import Transcripteur

RECORDINGS_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'recordings')
)
MIDI_TRANSCRIPTION_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'MIDI')
)
os.makedirs(MIDI_TRANSCRIPTION_PATH, exist_ok=True)

class Module5Screen(BaseScreen):
    def __init__(self):
        super().__init__()

        self.trans = Transcripteur()
        self.selected_audio = None
        self.selected_index = 0

        self.layout.setContentsMargins(40, 30, 40, 30)
        self.layout.setSpacing(20)

        # Title
        title = QLabel("Pick a song to transcribe")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: #5d8271;
        """)
        self.layout.addWidget(title)

        # Scroll area for recording list
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
        self.recordings = sorted(f for f in os.listdir(RECORDINGS_PATH) if f.endswith('.wav'))

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        self.list_layout = QVBoxLayout()  # Renamed properly here
        self.list_layout.setSpacing(10)
        scroll_content.setLayout(self.list_layout)
        scroll_area.setWidget(scroll_content)
        self.layout.addWidget(scroll_area, alignment=Qt.AlignHCenter)

        self._populate_recordings()

        # Transcribe button
        self.btn_transcribe = QPushButton("Transcribe → MIDI")
        self.btn_transcribe.setFixedHeight(40)
        self.btn_transcribe.setFixedWidth(250)
        self.btn_transcribe.setStyleSheet("""
            background-color: #5d8271;
            color: white;
            border-radius: 12px;
            font-weight: bold;
            font-size: 16px;
        """)
        self.btn_transcribe.clicked.connect(self._transcribe_selected)
        self.layout.addWidget(self.btn_transcribe, alignment=Qt.AlignCenter)

        # Success label
        self.success_label = QLabel("")
        self.success_label.setAlignment(Qt.AlignCenter)
        self.success_label.setStyleSheet("""
            color: #2e7d32;
            font-size: 18px;
        """)
        self.success_label.hide()
        self.layout.addWidget(self.success_label)

    def _populate_recordings(self):
        # Clear existing buttons
        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # Add buttons for each recording
        for i, fname in enumerate(self.recordings):
            btn = QPushButton(fname)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFlat(True)
            btn.setFixedWidth(500)
            btn.setStyleSheet(self._button_style(i == self.selected_index))
            btn.clicked.connect(lambda _, f=fname, idx=i: self._select_recording(f, idx))
            self.list_layout.addWidget(btn)

    def _button_style(self, selected):
        base = """
            QPushButton {
                background-color: #5d8271;
                color: white;
                border-radius: 10px;
                padding: 8px 15px;
                text-align: left;
                font-weight: normal;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #4a6a56;
            }
        """
        if selected:
            base += """
                QPushButton {
                    background-color: #34543f;
                    font-weight: bold;
                    font-size: 14px;
                }
            """
        return base

    def _select_recording(self, filename, index):
        self.selected_audio = os.path.join(RECORDINGS_PATH, filename)
        self.selected_index = index
        self.success_label.hide()
        self._populate_recordings()

    def _transcribe_selected(self):
        if not self.selected_audio:
            QMessageBox.warning(self, "No selection", "Please select a wav file to transcribe.")
            return

        try:
            self.trans.selectInputFile(self.selected_audio)
            self.trans.getNotesFromFile()

            base_name = os.path.splitext(os.path.basename(self.selected_audio))[0]
            output_midi = os.path.join(MIDI_TRANSCRIPTION_PATH, f"{base_name}.mid")

            self.trans.selectOutputFile(output_midi)
            self.trans.transcript()

            self.success_label.setText("Your wav was successfully transcribed!")
            self.success_label.show()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to transcribe:\n{e}")
