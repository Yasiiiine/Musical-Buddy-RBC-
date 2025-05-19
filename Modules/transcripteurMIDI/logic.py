from midiutil import MIDIFile
from midiutil.MidiFile import SHARPS,FLATS,MAJOR,MINOR
from scipy.io.wavfile import read
from Modules.tuner.TunerObject import NoteFinder

class Transcripteur:
    def __init__(self):
        self.dicoNote = {'C':0, 'C#':1, 'D':2, 'D#':3, 'E':4, 'F':5, 'F#':6, 'G':7, 'G#':8, 'A':9, 'A#':10, 'B':11}
        self.noteTool = NoteFinder()
        self.midifile = MIDIFile(1)
        
        self.PathfileToRead = "eqt-major-sc.wav"
        self.outputFile = "newMidi.mid"
        
        self.arrayNotes = []
        self.duration = []
        self.times = []
        self.volumes = []
        self.tempo = 60
        self.timeSignature = (4,2)
        self.keySignature = (0,SHARPS,MAJOR)
        
    def selectInputFile(self, InputFilePath = "."):
        self.PathfileToRead = InputFilePath
        return
    
    def selectOutputFile(self, OutputFilePath = "newMidi.mid"):
        self.outputFile = OutputFilePath
        return
    
    def transcript(self): 
        self.midifile.addKeySignature(0, 0, self.keySignature[0], self.keySignature[1], self.keySignature[2])
        self.midifile.addTempo(0, 0, self.tempo)
        self.midifile.addTimeSignature(0, 0, self.timeSignature[0], self.timeSignature[1], 24)

        for i in range(len(self.arrayNotes)):
            self.midifile.addNote(0, 0, self.arrayNotes[i], self.times[i], self.duration[i], 60) # '60' à remplaer par le self.volumes[i] si on tient compte du volume
        
        with open(self.outputFile, "wb") as output_file:
            self.midifile.writeFile(output_file)
            output_file.close()
        self.midifile = MIDIFile(1)
        return
    
    def getNotesFromFile(self): #Algortihme à finir: bonne découpe du signal et bon pas de temps/durée pour le parcours.
        
        #Découper le signal audio
        rate, signal = read(self.PathfileToRead)
        signalDecoupe = [signal[i: i + int(floor(rate*60/(self.tempo/16)))] for i in range(0,len(signal),int(floor(rate*60/(self.tempo/16))))]

        #Parcours du signal découpé
        # # Initialisation
        Seuil = 15 #Seuil d'amplitude pour compter une note. L'amplitude examinée est celle de la fréquence maximale de la DSE.
        CD = 0 # Durée de la note courante (Current Duration)
        CT = 0 # Temps courant dans la portée (Current Time)
        CN = 69 # Note courante (Current Note)
        arrayNote = []
        arrayDuration = []
        arrayTime = []

        # # Parcours
        for i in range(len(signalDecoupe)):
            self.noteTool.getNote(rate,signalDecoupe[i])
            Amp = self.noteTool.currentAmplitude
            NoteMIDI = (self.noteTool.currentOrdre + 1)*12 + self.dicoNote[self.noteTool.currentNote]

            if Amp < Seuil:
                if CD != 0:
                    arrayDuration.append(CD)
                    CD = 0
            else:
                if NoteMIDI == CN:
                    CD += 1/16
                else:
                    CN = NoteMIDI
                    arrayNote.append(CN)
                    arrayTime.append(CT)
                    if CD != 0:
                        arrayDuration.append(CD)
                    CD = 1/16
            CT += 1/16
        
        #Fin: Obtenir la durée de la dernière note si ce n'est pas un silence
        if CD != 0:
            arrayDuration.append(CD)

        #Mise à jour des paramètres du Transcripteur
        self.arrayNotes = arrayNote
        self.duration = arrayDuration
        self.times = arrayTime
        return
    
    def testAlgorithme(self): #Algorithme fonctionnel
        #Signal test ( tableau [(Amplitude,Note)] )
        signalAudioTest = [(0,69), (15,69), (15,69), (13,68), (15,68), (16,68), (23,60), (23,60), (23,60), (0,69), (16,75), (16,75)]

        Seuil = 15
        CD = 0
        CT = 0
        CN = 69
        arrayNote = []
        arrayDuration = []
        arrayTime = []
        for i in range(len(signalAudioTest)):
            Amp = signalAudioTest[i][0]
            NoteMIDI = signalAudioTest[i][1]
            if Amp < Seuil:
                if CD != 0:
                    arrayDuration.append(CD)
                    CD = 0
                CN = 0
            else:
                if NoteMIDI == CN:
                    CD += 1/16
                else:
                    CN = NoteMIDI
                    arrayNote.append(CN)
                    arrayTime.append(CT)
                    if CD != 0:
                        arrayDuration.append(CD)
                    CD = 1/16
            CT += 1/16
        if CD != 0:
            arrayDuration.append(CD)
        self.arrayNotes = arrayNote
        self.duration = arrayDuration
        self.times = arrayTime
        return
    
    def testTranscript(self): #Fonctionnel
        times = [i/5 for i in range(0,10)]
        durations = [1/5 for i in range(1,11)]
        volumes = [60 for i in range(1,11)]
        pitches = [60,62,64,66,67,69,71,72,74,76]

        self.arrayNotes = pitches
        self.times = times
        self.duration = durations
        self.volumes = volumes

        self.transcript()
        return