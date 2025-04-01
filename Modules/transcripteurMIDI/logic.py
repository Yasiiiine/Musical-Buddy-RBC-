import midiutil as mt
class Transcripteur:
    def __init__(self,path=""):
        self.arrayNotes = []
        self.tempo = 60
        self.duration = []
        self.times = []
        self.path = path
        self.outputFile = open(self.path)
    def transcript(self):
        midi = ...
        track    = 0   
        channel  = 0  
        
        for i in range(len(self.arrayNotes)):
            pitch = self.arrayNotes[i]
            time = self.times[i]
            duration = self.duration[i]
            volume   = 80 # Volume constant
            mt.addNote(track,channel,pitch,time,duration,volume)

        mt.writeFile(midi)