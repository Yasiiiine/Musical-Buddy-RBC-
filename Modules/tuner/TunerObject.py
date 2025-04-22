from numpy.fft import fft
from numpy import argmax, log2, abs as np_abs


class NoteFinder:
    def __init__(self):
        self.notes = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]
        self.currentNote = "A"
        self.currentFreq = 440
        self.currentOrdre = 4
        self.currentEcart = 0

    def getNote(self, freqEchantillonnage, signalAudio):
        dse = np_abs(fft(signalAudio)) * 2
        dse = dse[:len(dse) // 2]
        if dse.max() < 0.01:
            return  # ignore low amplitude noise

        self.currentFreq = argmax(dse) * freqEchantillonnage / len(signalAudio)
        floatOrdre = log2(self.currentFreq / 440) * 12
        self.currentOrdre = round(floatOrdre) // 12
        self.currentEcart = floatOrdre - round(floatOrdre)
        self.currentNote = self.notes[round(floatOrdre) % 12]
