# core/audio_screen.py
from core.base_screen import BaseScreen

class AudioScreen(BaseScreen):
    def __init__(self):
        super().__init__()
        self.setup_audio()

    def setup_audio(self):
        pass  # override in subclass

    def handle_key_input(self, event):
        pass  # optional: override for recording/volume, etc.
