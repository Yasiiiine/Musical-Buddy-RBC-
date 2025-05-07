from numpy.fft import fft
from numpy import argmax, log2, floor

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
        self.currentAmplitude = max(signalAudio)
        
        dse = abs(fft(signalAudio)) * 2
        dse = dse[:len(dse) // 2]
        if dse.max() < 0.01:
            return  # ignore low amplitude noise

        self.amp = floor(log2(max(signalAudio) + 1))
        dse = abs((fft(signalAudio)))*2 #Obtient la densité spectrale d'énergie du signal audio, ( l'amplitude des différentes fréquences)
        dse = dse[:len(dse)//2] # Ne prend que la partie de droite ( sinon le spectre est pair et 0 est au centre du vecteur )

       
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
        

class ChordFinder(NoteFinder):
    def __init__(self):
        super().__init__()
        self.f0 = 0
        self.f1 = 0
        self.f2 = 0

        # self.ordre0 = 0
        # self.ordre1 = 0
        # self.ordre2 = 0

        self.note0 = 0
        self.note1 = 0
        self.note2 = 0
    
    def getChord(self,freqEchantillonnage,signalAudio):
        
        dse = abs((fft(signalAudio)))*2
        dse = dse[:len(dse)//2]

        maxIndex = argmax(dse)
        
        self.currentFreq = maxIndex*freqEchantillonnage/len(dse)
        floatOrdre = log2(self.currentFreq/440)*12
        self.f0 = round(floatOrdre)
        self.note0 = self.notes[self.f0%12]

        for i in range(maxIndex - round(len(dse)/freqEchantillonnage), maxIndex + round(len(dse)/freqEchantillonnage) + 1):
            dse[i] = 0
        
        maxIndex = argmax(dse)
        
        self.currentFreq = maxIndex*freqEchantillonnage/len(dse)
        floatOrdre = log2(self.currentFreq/440)*12
        self.f1 = round(floatOrdre)
        self.note1 = self.notes[self.f1%12]

        for i in range(maxIndex - round(len(dse)/freqEchantillonnage), maxIndex + round(len(dse)/freqEchantillonnage) + 1):
            dse[i] = 0

        maxIndex = argmax(dse)
        
        self.currentFreq = maxIndex*freqEchantillonnage/len(dse)
        floatOrdre = log2(self.currentFreq/440)*12
        self.f2 = round(floatOrdre)
        self.note2 = self.notes[self.f2%12]

        for i in range(maxIndex - round(len(dse)/freqEchantillonnage), maxIndex + round(len(dse)/freqEchantillonnage) + 1):
            dse[i] = 0


        temp = (min(self.f0,self.f1),max(self.f0,self.f1))
        temp2 = (min(temp,self.f2),)

        

