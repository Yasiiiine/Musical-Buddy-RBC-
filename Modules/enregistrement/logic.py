
import sounddevice as sd
import numpy as np
import wave
from PyQt5.QtCore import QObject, QTimer, pyqtSignal
import Modules.enregistrement.config as cfg
import os
import datetime

class Recorder(QObject):

    recording_too_short = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.recording = False
        self.short_recording = False
        self.frames = []
        self.timer = QTimer()

    def toggle_recording(self):
        if self.recording:
            self.stop()
        else:
            self.start()

    def start(self):
        self.frames = []

        # Recherche d'un périphérique d'entrée valide
        input_devices = [
            i for i, dev in enumerate(sd.query_devices())
            if dev['max_input_channels'] > 0
        ]

        if not input_devices:
            print("Aucun périphérique d'entrée audio trouvé.")
            return

        input_device_index = input_devices[1]
        print(f"🎤 Micro utilisé : {sd.query_devices()[input_device_index]['name']}")

        self.stream = sd.InputStream(
            samplerate=cfg.RATE,
            channels=cfg.CHANNELS,
            dtype=cfg.FORMAT,
            blocksize=cfg.CHUNK,
            callback=self.callback,
            device=(input_device_index, None)  # entrée explicite
        )

        self.stream.start()
        self.timer.start(50)
        self.recording = True

    def stop(self):
        self.timer.stop()
        self.stream.stop()
        self.stream.close()
        self.save()
        self.recording = False

    def callback(self, indata, frames, time, status):
        if status:
            print(status)
        self.frames.append(indata.copy())

    def save(self):
        audio = np.concatenate(self.frames, axis=0)
        duration_seconds = len(audio) / cfg.RATE
        if duration_seconds<=1.5:
            print("Fichier trop court")
            self.short_recording = True
            self.recording_too_short.emit()
        else:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recording_{timestamp}.wav"
            filepath = os.path.join(cfg.OUTPUT_DIR, filename)

            os.makedirs(cfg.OUTPUT_DIR, exist_ok=True)

            with wave.open(filepath, 'wb') as wf:
                wf.setnchannels(cfg.CHANNELS)
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(cfg.RATE)
                wf.writeframes(audio.tobytes())

            print(f"Fichier enregistré : {filepath}")