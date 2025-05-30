# Modules/transcripteurMIDI/ui.py

import os
from PyQt5.QtWidgets import (
    QLabel, QVBoxLayout, QPushButton, QHBoxLayout,
    QFileDialog, QMessageBox, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt
from core.base_screen import BaseScreen
from Modules.transcripteurMIDI.logic import Transcripteur
import Modules.transcripteurMIDI.config as cfg

# corrected path into Assets/recordings
RECORDINGS_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__),
                 '..', '..', 'Assets', 'recordings')
)

class Module5Screen(BaseScreen):
    def __init__(self):
        super().__init__()

        # transcription engine
        self.trans = Transcripteur()
        self.transcript_done = False

        # --- Title ---
        title = QLabel(cfg.MODULE_LABEL)
        title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(title)

        # --- Existing recordings list (3 at a time) ---
        self.recordings      = sorted(f for f in os.listdir(RECORDINGS_PATH) if f.endswith('.wav'))
        self.selected_index  = 0
        self.visible_start   = 0
        self.items_per_page  = 3

        self.list_layout = QVBoxLayout()
        self.list_layout.setSpacing(8)
        self.layout.addLayout(self.list_layout)
        self._refresh_recording_buttons()

        # --- Upload / Record stub ---
        hr = QHBoxLayout()
        btn_up = QPushButton("Upload Audio")
        btn_up.clicked.connect(self._upload_audio)
        btn_rec = QPushButton("Record Audio")
        btn_rec.clicked.connect(self._record_audio)
        hr.addWidget(btn_up)
        hr.addWidget(btn_rec)
        self.layout.addLayout(hr)

        # --- Transcribe button ---
        self.btn_trans = QPushButton("Transcribe → MIDI")
        self.btn_trans.clicked.connect(self._do_transcribe)
        self.layout.addWidget(self.btn_trans, alignment=Qt.AlignCenter)

        # --- MIDI playback / save ---
        hb2 = QHBoxLayout()
        self.btn_play = QPushButton("▶ Play MIDI")
        self.btn_save = QPushButton("💾 Save MIDI")
        self.btn_play.clicked.connect(self._play_midi)
        self.btn_save.clicked.connect(self._save_midi)
        hb2.addWidget(self.btn_play)
        hb2.addWidget(self.btn_save)
        # push them down
        self.layout.addItem(QSpacerItem(0,20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        self.layout.addLayout(hb2)

        # internal state
        self.audio_path = None
        self.midi_path  = None

    def _refresh_recording_buttons(self):
        # clear old
        while self.list_layout.count():
            w = self.list_layout.takeAt(0).widget()
            if w: w.deleteLater()

        end = min(self.visible_start + self.items_per_page, len(self.recordings))
        for idx in range(self.visible_start, end):
            fname = self.recordings[idx]
            btn = QPushButton(fname)
            btn.clicked.connect(lambda _, f=fname: self._select_recording(f))
            # highlight
            if idx == self.selected_index:
                btn.setStyleSheet("background-color:#555; color:#fff;")
            self.list_layout.addWidget(btn)

    def _select_recording(self, fname):
        self.selected_index = self.recordings.index(fname)
        # adjust window
        if self.selected_index < self.visible_start:
            self.visible_start = self.selected_index
        elif self.selected_index >= self.visible_start + self.items_per_page:
            self.visible_start = self.selected_index - self.items_per_page + 1

        self.audio_path = os.path.join(RECORDINGS_PATH, fname)
        self.transcript_done = False
        self._refresh_recording_buttons()

    def _upload_audio(self):
        path, _ = QFileDialog.getOpenFileName(self,
            "Select Audio File", "", "Audio Files (*.wav *.mp3)")
        if not path:
            return
        self.audio_path     = path
        self.selected_index = -1
        self.transcript_done = False
        self._refresh_recording_buttons()

    def _record_audio(self):
        QMessageBox.information(self, "Record", "Recording not yet implemented here.")

    def _do_transcribe(self):
        if not self.audio_path:
            QMessageBox.warning(self, "No audio", "Please select or upload an audio file first.")
            return

        try:
            # feed paths into your logic
            self.trans.selectInputFile(self.audio_path)
            self.trans.getNotesFromFile()

            # ask where to save
            out, _ = QFileDialog.getSaveFileName(
                self, "Save MIDI as…",
                cfg.DEFAULT_OUTPUT, "MIDI Files (*.mid)")
            if not out:
                return

            self.trans.selectOutputFile(out)
            self.trans.transcript()

            self.midi_path      = out
            self.transcript_done = True
            QMessageBox.information(self, "Success", f"MIDI saved to:\n{out}")

        except Exception as err:
            QMessageBox.critical(self, "Transcription Error", str(err))

    def _play_midi(self):
        if not self.transcript_done:
            QMessageBox.warning(self, "Not ready", "Please transcribe first.")
            return
        # TODO: hook up real playback (e.g. pygame.midi)
        QMessageBox.information(self, "Play MIDI", "Playback not yet implemented.")

    def _save_midi(self):
        if not self.transcript_done:
            QMessageBox.warning(self, "Not ready", "Please transcribe first.")
            return
        # already saved in _do_transcribe()
        QMessageBox.information(self, "Saved", f"Already saved to:\n{self.midi_path}")

    def keyPressEvent(self, ev):
        # scroll list
        if ev.key() == Qt.Key_Up and self.selected_index > 0:
            self.selected_index -= 1
            if self.selected_index < self.visible_start:
                self.visible_start -= 1
            self._refresh_recording_buttons()

        elif ev.key() == Qt.Key_Down and self.selected_index < len(self.recordings) - 1:
            self.selected_index += 1
            if self.selected_index >= self.visible_start + self.items_per_page:
                self.visible_start += 1
            self._refresh_recording_buttons()

        elif ev.key() in (Qt.Key_Return, Qt.Key_Enter):
            if 0 <= self.selected_index < len(self.recordings):
                self._select_recording(self.recordings[self.selected_index])

        else:
            super().keyPressEvent(ev)
