from midiutil import MIDIFile
from midiutil.MidiFile import SHARPS,FLATS,MAJOR,MINOR
from scipy.io.wavfile import read
from Modules.tuner.TunerObject import NoteFinder
from numpy import floor

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
        self.tempo = 40
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
        signal = signal[:,0]
        pas = int(floor(rate*60/(self.tempo*16)))
        signalDecoupe = [signal[i: i + pas] for i in range(0,len(signal),pas)]

        #Parcours du signal découpé
        # # Initialisation
        Seuil = 15
        CD = 0
        CT = 0
        CN = 69
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
        
        if CD != 0:
            arrayDuration.append(CD)

        self.arrayNotes = arrayNote
        self.duration = arrayDuration
        self.times = arrayTime
        return