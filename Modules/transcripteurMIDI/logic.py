# Modules/transcripteurMIDI/logic.py

from midiutil import MIDIFile
from scipy.io.wavfile import read
from Modules.tuner.TunerObject import NoteFinder
from numpy import floor, log2

class Transcripteur:
    def __init__(self):
        # semitone offsets within an octave
        self.dicoNote = {
            'C':0, 'C#':1, 'D':2, 'D#':3, 'E':4,
            'F':5, 'F#':6, 'G':7, 'G#':8, 'A':9,
            'A#':10,'B':11
        }
        self.noteTool = NoteFinder()
        self.midifile = MIDIFile(1)

        # input/output paths set by UI
        self.PathfileToRead = "eqt-major-sc.wav"
        self.outputFile     = "newMidi.mid"

        # results
        self.arrayNotes = []
        self.times      = []
        self.duration   = []

        # parameters
        self.tempo            = 40      # BPM
        self.silenceThreshold = 15      # amplitude below which we consider “silence”
        self.min_silence      = 2       # require this many consecutive silent blocks before closing note

    def selectInputFile(self, path):
        self.PathfileToRead = path

    def selectOutputFile(self, path):
        self.outputFile = path

    def transcript(self):
        """Write out absolute‐pitch MIDI (no key signature)."""
        # only set tempo; no key or time signature
        self.midifile.addTempo(0, 0, self.tempo)

        for pitch, start, dur in zip(self.arrayNotes, self.times, self.duration):
            self.midifile.addNote(
                track=0, channel=0,
                pitch=pitch,
                time=start,
                duration=dur,
                volume=100
            )

        with open(self.outputFile, "wb") as f:
            self.midifile.writeFile(f)

        # reset for next run
        self.midifile = MIDIFile(1)

    def getNotesFromFile(self):
        """Fill self.arrayNotes, self.times, self.duration with absolute‐pitch data."""
        rate, signal = read(self.PathfileToRead)

        # stereo → mono
        if signal.ndim > 1:
            signal = signal[:,0]

        # block size so that 16 blocks = 1 beat
        block_size = int(floor(rate * 60 / (self.tempo * 16)))
        blocks = [
            signal[i:i+block_size]
            for i in range(0, len(signal), block_size)
        ]

        notes, times, durs = [], [], []
        CD, CT = 0.0, 0.0               # current duration, current beat‐time
        current_pitch = None
        silence_count = 0

        for blk in blocks:
            # detect pitch & amplitude
            self.noteTool.getNote(rate, blk)
            amp  = self.noteTool.currentAmplitude
            # compute absolute MIDI from frequency if available, else from octave+note
            freq = getattr(self.noteTool, "currentFrequency", None)
            if freq and freq > 0:
                midi = int(round(69 + 12 * log2(freq / 440.0)))
            else:
                midi = (
                    (self.noteTool.currentOrdre + 1) * 12
                    + self.dicoNote[self.noteTool.currentNote]
                )

            if amp < self.silenceThreshold:
                # accumulate silence
                silence_count += 1
                if silence_count >= self.min_silence and CD > 0:
                    # close out the note
                    notes.append(current_pitch)
                    times.append(CT - CD)
                    durs.append(CD)
                    CD = 0.0
                    current_pitch = None
            else:
                # audible block
                silence_count = 0
                if current_pitch is None:
                    # start brand new note
                    current_pitch = midi
                    CD = 1/16
                elif midi == current_pitch:
                    # same note, extend
                    CD += 1/16
                else:
                    # pitch changed abruptly: close old and open new
                    notes.append(current_pitch)
                    times.append(CT - CD)
                    durs.append(CD)

                    current_pitch = midi
                    CD = 1/16

            CT += 1/16

        # flush final note
        if CD > 0 and current_pitch is not None:
            notes.append(current_pitch)
            times.append(CT - CD)
            durs.append(CD)

        self.arrayNotes = notes
        self.times      = times
        self.duration   = durs
