# config.py
import os

MODULE_COLOR = "#ffcccc"  # couleur unique
MODULE_LABEL = "Transcripteur MIDI"
TEMPO = 60
RECORDINGS_PATH = os.path.normpath(
    os.path.join(os.path.dirname(__file__),
                 '..', '..', 'recordings')
)

# Where to write out your .mid files, by default
OUTPUT_DIR = os.path.normpath(
    os.path.join(os.path.dirname(__file__),
                 '..', '..', 'MIDI')
)

# Pre‐filled filename in the "Save As..." dialog
DEFAULT_OUTPUT = os.path.join(OUTPUT_DIR, "transcription.mid")

# Transcription parameters
SILENCE_THRESHOLD = 1000    # amplitude below this is considered silence
SHARPS = 0                # key signature, 0 for C major