import sounddevice as sd
import numpy as np
import wave
from PyQt5.QtCore import QObject, QTimer, pyqtSignal
import os
import Modules.enregistrement.config as cfg
from AudioSettingsManager import AudioSettingsManager

class Recorder(QObject):
    recording_too_short = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.recording = False
        self.short_recording = False
        self.frames = []
        self.timer = QTimer()
        self.timer.timeout.connect(self._on_timer)
        self.soundlevel = 0
        self.stream = None

        # Ensure the output directory exists
        os.makedirs(cfg.OUTPUT_DIR, exist_ok=True)

    def toggle_recording(self):
        if self.recording:
            self.stop()
        else:
            self.start()

    def start(self):
        self.frames = []
        self.recording = True
        self.short_recording = False

        try:
            device = AudioSettingsManager.get_input_device()
            self.stream = sd.InputStream(
                samplerate=cfg.RATE,
                channels=cfg.CHANNELS,
                dtype=cfg.FORMAT,
                blocksize=cfg.CHUNK,
                callback=self.callback,
                device=device
            )
            self.stream.start()
            self.timer.start(50)
            print(f"Recording from device {device}")
        except Exception as e:
            print(f"Error starting recording: {e}")
            self.recording = False

    def stop(self):
        try:
            self.timer.stop()
            if self.stream:
                self.stream.stop()
                self.stream.close()
            self.recording = False
            self.save()
        except Exception as e:
            print(f"Error stopping recording: {e}")

    def callback(self, indata, frames, time, status):
        if status:
            print(f"Stream status: {status}")
        self.frames.append(indata.copy())
        self.soundlevel = float(np.max(np.abs(indata)))

    def _on_timer(self):
        pass

    def get_next_filename(self):
        existing_files = os.listdir(cfg.OUTPUT_DIR)
        used_indices = [int(f[:-4]) for f in existing_files if f.endswith('.wav') and f[:-4].isdigit()]
        next_index = 0
        while next_index in used_indices:
            next_index += 1
        return os.path.join(cfg.OUTPUT_DIR, f"{next_index}.wav")

    def save(self):
        try:
            audio = np.concatenate(self.frames, axis=0)
            duration_seconds = len(audio) / cfg.RATE
            if duration_seconds <= 1.5:
                print("Recording too short.")
                self.short_recording = True
                self.recording_too_short.emit()
                return

            filepath = self.get_next_filename()
            with wave.open(filepath, 'wb') as wf:
                wf.setnchannels(cfg.CHANNELS)
                wf.setsampwidth(2)
                wf.setframerate(cfg.RATE)
                wf.writeframes(audio.tobytes())

            print(f"Recording saved: {filepath}")
        except Exception as e:
            print(f"Error saving recording: {e}")
