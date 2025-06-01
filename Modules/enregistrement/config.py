OUTPUT_DIR     = "recordings/"
RATE           = 44100        # for MicRecorder
CHANNELS       = 1
CHUNK          = 1024         # for MicRecorder
FORMAT         = "int16"
MIN_LENGTH_SEC = 1.5          # threshold for “too short”

# ───– ADC constants ──────────────────────────────────────────────────────
ADC_RATE    = 8000           # sample ADC at 8 kHz
ADC_CHUNK   = 256            # read 256 samples per block
ADC_CHANNEL = 7              # your audio’s wired to MCP3008 CH7

