# Modules/transcripteurMIDI/ui.py

import os
from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QPushButton, QScrollArea,
    QHBoxLayout, QSizePolicy, QMessageBox
)
from PyQt5.QtCore import Qt, QEvent
from core.base_screen import BaseScreen
from core.styles import retro_label_font, bpm_label_style
from Modules.transcripteurMIDI.logic import Transcripteur

RECORDINGS_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'recordings')
)
os.makedirs(RECORDINGS_PATH, exist_ok=True)


class Module5Screen(BaseScreen):
    def __init__(self):
        super().__init__()

        # Transcription logic
        self.transcriber = Transcripteur()
        self.transcript_done = False

        # UI state
        self.recordings = sorted(f for f in os.listdir(RECORDINGS_PATH) if f.endswith('.wav'))
        self.selected_index = 0

        # --- Title ---
        self.title = QLabel("Pick a song to transcribe")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setFont(retro_label_font(32))
        self.title.setStyleSheet(bpm_label_style())
        self.layout.addWidget(self.title)

        # Spacer
        self.layout.addSpacing(20)

        # --- Scroll area for recordings ---
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
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        self.buttons_layout = QVBoxLayout()
        self.buttons_layout.setSpacing(10)
        container.setLayout(self.buttons_layout)
        scroll_area.setWidget(container)

        # Limit visible height to 3 items (approx 3 × 50px)
        scroll_area.setFixedHeight(3 *  50 + 10)  # Replace Fifty with desired height constant, e.g., 50

        self.layout.addWidget(scroll_area, alignment=Qt.AlignHCenter)

        # Spacer
        self.layout.addSpacing(20)

        # --- Transcribe Button ---
        self.transcribe_btn = QPushButton("Transcribe → MIDI")
        self.transcribe_btn.setFixedSize(200, 40)
        self.transcribe_btn.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                background-color: #5d8271;
                color: white;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #4a6b5c;
            }
            QPushButton:pressed {
                background-color: #3f5a4b;
            }
        """)
        self.transcribe_btn.clicked.connect(self._on_transcribe)
        self.layout.addWidget(self.transcribe_btn, alignment=Qt.AlignCenter)

        # Spacer
        self.layout.addSpacing(20)

        # --- Success Label ---
        self.success_label = QLabel("")
        self.success_label.setAlignment(Qt.AlignCenter)
        self.success_label.setStyleSheet("""
            color: #2e7d32;
            font-size: 18px;
        """)
        self.success_label.hide()
        self.layout.addWidget(self.success_label)

        # Final setup
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

        self._populate_recording_buttons()

    def _button_style(self, selected: bool):
        base = """
            QPushButton {
                font-size: 14px;
                padding: 6px 12px;
                background-color: #5d8271;
                color: white;
                border: none;
                border-radius: 6px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #4a6b5c;
            }
        """
        if selected:
            base += """
                QPushButton {
                    background-color: #555555;
                    font-weight: bold;
                }
            """
        return base

    def _populate_recording_buttons(self):
        # Clear existing
        while self.buttons_layout.count():
            w = self.buttons_layout.takeAt(0).widget()
            if w:
                w.deleteLater()

        # Create a button for each recording
        for i, fname in enumerate(self.recordings):
            btn = QPushButton(self._shorten(fname, 40))
            btn.setFixedWidth(550)
            btn.setMinimumHeight(30)  # Replace Thirty with desired button height, e.g., 30
            btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            btn.setStyleSheet(self._button_style(i == self.selected_index))
            btn.installEventFilter(self)
            btn.clicked.connect(lambda _, idx=i: self._on_select(idx))
            # Container to center horizontally
            wrapper = QWidget()
            hl = QHBoxLayout()
            hl.setContentsMargins(0, 0, 0, 0)
            hl.addStretch()
            hl.addWidget(btn)
            hl.addStretch()
            wrapper.setLayout(hl)
            self.buttons_layout.addWidget(wrapper)

    def _shorten(self, text: str, max_len: int) -> str:
        return text if len(text) <= max_len else text[: max_len - 3] + "..."

    def _on_select(self, index: int):
        self.selected_index = index
        self.selected_audio = os.path.join(RECORDINGS_PATH, self.recordings[index])
        self.success_label.hide()
        self._populate_recording_buttons()

    def _on_transcribe(self):
        if not self.recordings:
            QMessageBox.warning(self, "No Recordings", "The recordings folder is empty.")
            return
        if self.selected_index < 0 or self.selected_index >= len(self.recordings):
            QMessageBox.warning(self, "No Selection", "Please select a .wav file first.")
            return

        fname = self.recordings[self.selected_index]
        audio_path = os.path.join(RECORDINGS_PATH, fname)

        try:
            # Perform transcription
            self.transcriber.selectInputFile(audio_path)
            self.transcriber.getNotesFromFile()
            midi_name = os.path.splitext(fname)[0] + ".mid"
            output_midi = os.path.join(RECORDINGS_PATH, midi_name)
            self.transcriber.selectOutputFile(output_midi)
            self.transcriber.transcript()

            self.success_label.setText(f"✓ Transcribed: {midi_name}")
            self.success_label.show()
            self.transcript_done = True

        except Exception as e:
            QMessageBox.critical(self, "Transcription Error", f"Failed to transcribe:\n{e}")

    def keyPressEvent(self, ev):
        if ev.key() == Qt.Key_Up and self.selected_index > 0:
            self.selected_index -= 1
            self._populate_recording_buttons()
        elif ev.key() == Qt.Key_Down and self.selected_index < len(self.recordings) - 1:
            self.selected_index += 1
            self._populate_recording_buttons()
        elif ev.key() in (Qt.Key_Return, Qt.Key_Enter):
            self._on_transcribe()
        else:
            super().keyPressEvent(ev)

    def eventFilter(self, source, event):
        # Hover highlights and moves selection
        if event.type() == QEvent.Enter and isinstance(source, QPushButton):
            for i in range(self.buttons_layout.count()):
                wrapper = self.buttons_layout.itemAt(i).widget()
                if wrapper:
                    btn = wrapper.layout().itemAt(1).widget()
                    if btn == source and self.selected_index != i:
                        # Reset previous
                        prev_wrap = self.buttons_layout.itemAt(self.selected_index).widget()
                        prev_btn = prev_wrap.layout().itemAt(1).widget()
                        prev_btn.setStyleSheet(self._button_style(False))
                        # Highlight new
                        btn.setStyleSheet(self._button_style(True))
                        self.selected_index = i
                        break
        return super().eventFilter(source, event)
