from numpy import fft,log2,argmax

def getNote(self, freqEchantillonnage, signalAudio):

        dse = abs((fft(signalAudio)))*2
        dse = dse[:len(dse)//2]

        
        self.currentFreq = argmax(dse)*freqEchantillonnage/len(dse)
        floatOrdre = log2(self.currentFreq/440)*12
        self.currentOrdre = round(floatOrdre)//12
        self.currentEcart = floatOrdre - round(floatOrdre)
        self.currentNote = self.notes[round(floatOrdre)%12]
        