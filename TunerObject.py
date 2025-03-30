# from scipy.io.wavfile import read
from numpy.fft import fft
from numpy import argmax, log2


class NoteFinder:
    def __init__(self):
        self.notes  = ["A","A#","B","C","C#","D","D#","E","F","F#","G","G#"]
        self.currentNote = "A"
        self.currentFreq = 440
        self.currentOrdre = 4
        self.currentEcart = res
    

    def getNote(self, freqEchantillonnage, signalAudio):

        dse = abs((fft(signalAudio)))*2
        dse = dse[:len(dse)//2]

        freqMax = argmax(dse)*freqEchantillonnage/len(dse)

        freqNorm = freqMax/440
        ordre = log2(freqNorm)
        res = ordre*12
        noteTh = self.notes[round(res)]

        return freqMax, ordre, res, noteTh


# rate, signal = read("ProtestMonoBruitTronque.wav")
# tuner = NoteFinder()
# freq, ordre, res, noteTh = tuner.getNote(rate,signal)

# print("min : ", int(2**((round(res) -0.1)/12)*440), "note: ", tuner.notes[round(res)], " max: ", int(2**((round(res) +0.1)/12)*440 + 3))


