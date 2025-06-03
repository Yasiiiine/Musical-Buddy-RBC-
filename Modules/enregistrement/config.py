# Modules/enregistrement/config.py
WINDOWS = True  # Set to True on Windows, False on Raspberry Pi
OUTPUT_DIR = "recordings/"  # Directory for WAV files
RATE = 44100
CHANNELS = 1
CHUNK = 1024
FORMAT = "int16"
MIN_LENGTH_SEC = 1.5
ADC_RATE = 8000
ADC_CHUNK = 256
ADC_CHANNEL = 7
PLAGES_NIVEAU_SONORE = [0, 1000, 5000, 10000, 20000, 30000]