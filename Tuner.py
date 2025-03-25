from scipy.io.wavfile import read
from scipy.fftpack import fft
from numpy import argmax, log2


notes  = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]

rate, signal = read("audiofile.wav")
dse = fft(signal,len(signal))**2
freqMax = argmax(dse)

freqNorm = freqMax/16.35
ordre = log2(freqNorm)

res = ordre/12




