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
        self.lock = threading.Lock()  # Add a lock to ensure thread-safe operations

    def play(self, filename):
        self.stop()
        # Ne pas refaire join ici, déjà fait dans stop()
        audio_file = os.path.join(self.recordings_path, filename)
        if os.path.exists(audio_file):
            data, self.sample_rate = sf.read(audio_file)
            if len(data.shape) > 1 and data.shape[1] > 1:
                data = data.mean(axis=1, keepdims=True)
            elif len(data.shape) == 1:
                data = data.reshape(-1, 1)
            with self.lock:
                self.audio_data = data
                self.stop_flag = False
                self.is_playing_flag = True
            self.playing_thread = threading.Thread(target=self._play_audio, daemon=True)
            self.playing_thread.start()
            print(f"Playing: {filename}")
        else:
            print(f"File not found: {audio_file}")

    def stop(self):
        with self.lock:
            self.stop_flag = True
        # Utilise un timeout pour ne pas bloquer l'UI
        if self.playing_thread and self.playing_thread.is_alive():
            self.playing_thread.join(timeout=1)
        with self.lock:
            self.is_playing_flag = False
        print("Playback stopped.")

    def _play_audio(self):
        try:
            def callback(outdata, frames, time, status):
                if status:
                    print(status)
                with self.lock:
                    if self.stop_flag or self.audio_data is None:
                        raise sd.CallbackStop()
                    samples_left = len(self.audio_data)
                    if samples_left < frames:
                        outdata[:samples_left] = self.audio_data[:samples_left].reshape(-1, outdata.shape[1])
                        if samples_left < frames:
                            outdata[samples_left:] = 0
                        self.audio_data = None
                        raise sd.CallbackStop()
                    else:
                        outdata[:] = self.audio_data[:frames].reshape(-1, outdata.shape[1])
                        self.audio_data = self.audio_data[frames:]

            with sd.OutputStream(samplerate=self.sample_rate, channels=1, callback=callback):
                # Boucle d'attente qui vérifie régulièrement le stop_flag
                while True:
                    with self.lock:
                        if self.stop_flag or self.audio_data is None:
                            break
                    sd.sleep(100)
        except sd.CallbackStop:
            pass
        except Exception as e:
            print(f"Error during playback: {e}")
        finally:
            with self.lock:
                self.is_playing_flag = False

    def is_playing(self):
        with self.lock:
            return self.is_playing_flag

    def get_duration(self):
        with self.lock:
            return int(len(self.audio_data) / self.sample_rate * 1000) if self.audio_data is not None else 0

    def get_time(self):
        print("Current playback time tracking is not supported with sounddevice.")
        return 0