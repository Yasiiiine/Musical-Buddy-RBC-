from numpy.fft import fft
from numpy import argmax, log2, floor, abs
from numpy import max as maxArray

#Classe trouvant une note dans un vecteur signalAudio échantillonné à la fréquence freqEchantillonnage

class NoteFinder:
    def __init__(self):
        self.freqOrdre = [15.88, 31.77, 63.55, 127.1,  254.2, 508.4, 1017, 2033, 4066, 8134]
        self.notes  = ["A","A#","B","C","C#","D","D#","E","F","F#","G","G#"] #notes possibles en chaîne de caractères
        self.currentNote = "A" #note courante
        self.currentFreq = 440 #fréquence de la note courante théorique
        self.currentOrdre = 4 #ordre de la note courante théorique
        self.currentEcart = 0 # écart à la fréquence théorique de la note la plus proche
        self.currentAmplitude = 0

    def getNote(self, freqEchantillonnage, signalAudio):
        self.currentAmplitude = maxArray(signalAudio)
        
        dse = abs(fft(signalAudio)) * 2
        dse = dse[:len(dse) // 2]
        if dse.max() < 0.01:
            return  # ignore low amplitude noise
           
        self.currentFreq = argmax(dse)*freqEchantillonnage/len(dse) #fréquence d'amplitude maximale du spectre (indice*fEchantillonnage/len(fft))
        if self.currentFreq == 0.0:
            self.currentFreq = 440
        # Toute fréquence de note peut s'écrire f = 440 * (2**(k/12)), 

        floatOrdre = log2(self.currentFreq/440)*12
        self.currentEcart = floatOrdre - round(floatOrdre)
        self.currentNote = self.notes[round(floatOrdre)%12]
        
        i = 0
        while i != 10 and self.currentFreq >= self.freqOrdre[i]:
            i += 1   
        if i == 0:
            self.currentOrdre = 0
        else: self.currentOrdre = (i-2)