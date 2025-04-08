# logic.py

import os
import vlc

class AudioPlayer:
    def __init__(self, recordings_path):
        self.recordings_path = recordings_path
        self.player = None

    def play(self, filename):
        if self.player is not None and self.player.is_playing():
            self.player.stop()

        audio_file = os.path.join(self.recordings_path, filename)
        if os.path.exists(audio_file):
            if self.player is None:
                self.player = vlc.MediaPlayer(audio_file)
            else:
                self.player.set_media(vlc.Media(audio_file))
            self.player.play()
            print(f"Playing: {filename}")
        else:
            print(f"File not found: {audio_file}")

    def pause(self):
        if self.player is not None and self.player.is_playing():
            self.player.pause()

    def resume(self):
        if self.player is not None:
            self.player.play()

    def stop(self):
        if self.player is not None and (self.player.is_playing() or self.is_paused()):
            self.player.stop()
            self.player = None  # Reset the player to ensure proper cleanup

    def is_playing(self):
        return self.player.is_playing() if self.player else False

    def is_paused(self):
        return self.player.get_state() == vlc.State.Paused if self.player else False

    def get_duration(self):
        return self.player.get_length() if self.player else 0

    def get_time(self):
        return self.player.get_time() if self.player else 0