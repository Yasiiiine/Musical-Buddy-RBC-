from scipy.io.wavfile import read
from numpy.fft import fft
from numpy import argmax, log2
import numpy as np

import PyQt5.QtWidgets
from PyQt5.QtWidgets import QLabel, QVBoxLayout,QWidget


notes  = ["A","A#","B","C","C#","D","D#","E","F","F#","G","G#",]

rate, signal = read("ProtestMonoBruitTronque.wav")
sigTronque = signal

dse = abs((fft(sigTronque)))*2
dse = dse[:len(dse)//2]


freqMax = argmax(dse)*rate/len(dse)

freqNorm = freqMax/440
ordre = log2(freqNorm)
res = ordre*12

"""print("freqMax: ", freqMax, " ", rate, "\n")
print("freqNorm: ", freqNorm, "\n")
print("ordre: ", ordre, "\n")
print("res: ", res, "\n")

print(round(res)/12)"""
print("min : ", int(2**((round(res) -0.1)/12)*440), "note: ", notes[round(res)], " max: ", int(2**((round(res) +0.1)/12)*440 + 3))


window = QWidget()
layout = QVBoxLayout()
labelNote = QLabel(layout)
renderArea = QWidget(layout)
renderArea.setPixmap
window.setLayout(layout)