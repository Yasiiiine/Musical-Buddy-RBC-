# audio_utils.py

import sounddevice as sd
from AudioSettingsManager import AudioSettingsManager

def initialize_audio_devices():
    """
    Reads the input/output indices from AudioSettingsManager and
    sets sd.default.device accordingly. Call this once at startup
    or whenever the user changes their selection.
    """
    in_idx = AudioSettingsManager.get_input_device()
    out_idx = AudioSettingsManager.get_output_device()

    # Retrieve current defaults (in case input is unchanged)
    prev_in, prev_out = sd.default.device

    # Only override if out_idx is not None
    if out_idx is not None:
        if in_idx is not None:
            sd.default.device = (in_idx, out_idx)
        else:
            sd.default.device = (prev_in, out_idx)
