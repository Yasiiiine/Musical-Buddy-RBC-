from scipy.io.wavfile import read
from numpy.fft import fft
from numpy import argmax, log2
from PyQt5.QtWidgets import QLabel, QVBoxLayout,QWidget,QMainWindow


notes  = ["A","A#","B","C","C#","D","D#","E","F","F#","G","G#",]

def getNote(freqEchantillonnage,signalAudio):

    dse = abs((fft(signalAudio)))*2
    dse = dse[:len(dse)//2]

    freqMax = argmax(dse)*freqEchantillonnage/len(dse)

    freqNorm = freqMax/440
    ordre = log2(freqNorm)
    res = ordre*12
    noteTh = notes[round(res)]

    return freqMax, ordre, res, noteTh

rate, signal = read("ProtestMonoBruitTronque.wav")

freq, ordre, res, noteTh = getNote(rate,signal)

print("min : ", int(2**((round(res) -0.1)/12)*440), "note: ", notes[round(res)], " max: ", int(2**((round(res) +0.1)/12)*440 + 3))




