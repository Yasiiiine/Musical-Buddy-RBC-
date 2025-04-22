import sounddevice as sd
import numpy as np
from numpy.fft import fft
from numpy import argmax, log2
import time


class NoteFinder:
    def __init__(self):
        self.notes = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]

    def get_note_name(self, fs, signal):
        spectrum = abs(fft(signal))[:len(signal) // 2]
        peak = argmax(spectrum)
        freq = peak * fs / len(signal)
        if freq <= 0:
            return None, 0
        diff = log2(freq / 440) * 12
        note = self.notes[round(diff) % 12]
        octave = round(diff) // 12 + 4
        return f"{note}{octave}", freq


def tuner_loop(device_index=1):
    fs = 44100
    blocksize = 4096
    threshold = 0.005
    stability = 5

    note_tool = NoteFinder()
    last_note = None
    count = 0

    print(f"\nUtilisation de l'entrée audio ID = {device_index}")
    print("Accordeur actif... (Ctrl+C pour quitter)\n")

    def callback(indata, frames, time_info, status):
        nonlocal last_note, count

        signal = indata[:, 0]
        if np.max(np.abs(signal)) < threshold:
            return

        note, freq = note_tool.get_note_name(fs, signal)
        if note is None:
            return

        if note == last_note:
            count += 1
        else:
            count = 0
            last_note = note

        if count >= stability:
            print(f"Note détectée : {note} ({freq:.1f} Hz)")
            count = 0

    try:
        with sd.InputStream(callback=callback, samplerate=fs, channels=1, blocksize=blocksize, device=(device_index, None)):
            while True:
                time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nAccordeur arrêté.")
    except Exception as e:
        print("Erreur :", e)


if __name__ == "__main__":
    tuner_loop(device_index=1)
