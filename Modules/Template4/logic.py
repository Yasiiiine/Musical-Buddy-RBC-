import os
import sounddevice as sd
import soundfile as sf
import threading


class AudioPlayer:
    def __init__(self, recordings_path):
        self.recordings_path = recordings_path
        self.audio_data = None
        self.sample_rate = None
        self.playing_thread = None
        self.is_playing_flag = False
        self.stop_flag = False

    def play(self, filename):
        self.stop()  # Stop any currently playing audio

        audio_file = os.path.join(self.recordings_path, filename)
        if os.path.exists(audio_file):
            self.audio_data, self.sample_rate = sf.read(audio_file)
            self.stop_flag = False
            self.is_playing_flag = True
            self.playing_thread = threading.Thread(target=self._play_audio)
            self.playing_thread.start()
            print(f"Playing: {filename}")
        else:
            print(f"File not found: {audio_file}")

    def _play_audio(self):
        def callback(outdata, frames, time, status):
            if status:
                print(status)
            if self.stop_flag or self.audio_data is None:
                raise sd.CallbackStop()
            outdata[:] = self.audio_data[:frames]
            self.audio_data = self.audio_data[frames:]

        with sd.OutputStream(samplerate=self.sample_rate, channels=len(self.audio_data.shape), callback=callback):
            sd.sleep(int(len(self.audio_data) / self.sample_rate * 1000))
        self.is_playing_flag = False

    def pause(self):
        print("Pause functionality is not supported with sounddevice.")

    def resume(self):
        print("Resume functionality is not supported with sounddevice.")

    def stop(self):
        self.stop_flag = True
        if self.playing_thread and self.playing_thread.is_alive():
            self.playing_thread.join()
        self.is_playing_flag = False
        print("Playback stopped.")

    def is_playing(self):
        return self.is_playing_flag

    def get_duration(self):
        return int(len(self.audio_data) / self.sample_rate * 1000) if self.audio_data is not None else 0

    def get_time(self):
        print("Current playback time tracking is not supported with sounddevice.")
        return 0