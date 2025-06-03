# Modules/enregistrement/logic.py

import threading
import time
import wave
import os
import json
import numpy as np
from PyQt5.QtCore import QObject, QTimer, pyqtSignal

import Modules.enregistrement.config as cfg

# Conditional imports for Linux (Raspberry Pi)
if not cfg.WINDOWS:
    try:
        import spidev  # For MCP3008 ADC access
        import scipy.signal  # Example scipy module; adjust based on your needs
    except ImportError as e:
        print(f"Warning: Failed to import platform-specific modules: {e}")
        cfg.WINDOWS = True  # Fallback to Windows mode if imports fail

# Microphone recording is supported on all platforms
try:
    import sounddevice as sd  # For microphone capture
except ImportError as e:
    print(f"Error: sounddevice module is required: {e}")
    raise

def get_next_counter(counter_type):
    """
    Read and increment the counter for the given type ('mic' or 'adc') from counter.txt.
    Returns the next counter value and updates the file.
    """
    counter_file = os.path.join(cfg.OUTPUT_DIR, "counter.txt")
    counters = {"mic": 0, "adc": 0}  # Default counters

    # Create OUTPUT_DIR if it doesn't exist
    os.makedirs(cfg.OUTPUT_DIR, exist_ok=True)

    # Read existing counters
    try:
        with open(counter_file, "r") as f:
            counters = json.load(f)
            if not isinstance(counters, dict) or counter_type not in counters:
                counters = {"mic": 0, "adc": 0}
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    # Get and increment the counter for the given type
    next_counter = counters[counter_type] + 1
    counters[counter_type] = next_counter

    # Save updated counters
    try:
        with open(counter_file, "w") as f:
            json.dump(counters, f)
    except Exception as e:
        print(f"Error saving counter file: {e}")

    return next_counter

class MicRecorder(QObject):
    """
    Recorder that captures from the default system mic (via sounddevice)
    and writes a 16-bit WAV at cfg.RATE (e.g. 44100 Hz). Emits 'recording_too_short'
    if total duration ≤ cfg.MIN_LENGTH_SEC, and 'recording_saved' with filename when saved.
    """
    recording_too_short = pyqtSignal()
    recording_saved = pyqtSignal(str)  # Emits filename of saved recording

    def __init__(self):
        super().__init__()
        self.recording = False
        self.frames = []  # List of numpy arrays (int16)
        self.short_recording = False
        self.soundlevel = 0.0  # For UI meter
        self._stream = None
        self._lock = threading.Lock()

        # Qt timer for UI updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_ui)
        self.timer.start(50)  # Every 50 ms

    def _update_ui(self):
        # Placeholder for UI updates (e.g., level meter)
        pass

    def toggle_recording(self):
        if self.recording:
            self.stop()
        else:
            self.start()

    def start(self):
        """Start capturing from microphone."""
        if self.recording:
            return

        self.frames = []
        self.short_recording = False
        self.recording = True

        # Open sounddevice InputStream
        self._stream = sd.InputStream(
            samplerate=cfg.RATE,
            channels=cfg.CHANNELS,
            dtype=cfg.FORMAT,
            blocksize=cfg.CHUNK,
            callback=self._audio_callback
        )
        self._stream.start()
        print("Mic recording started.")

    def _audio_callback(self, indata, frames, time_info, status):
        """
        Callback runs in sounddevice’s audio thread.
        Append each incoming block to self.frames.
        """
        with self._lock:
            self.frames.append(indata.copy().reshape(cfg.CHUNK))
            lvl = np.max(np.abs(indata))
            self.soundlevel = float(lvl)

    def stop(self):
        """Stop input stream, write WAV, or emit 'too short'."""
        if not self.recording:
            return

        self.recording = False
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None

        # Concatenate all chunks
        with self._lock:
            try:
                all_samples = np.concatenate(self.frames)
            except ValueError:
                all_samples = np.zeros(0, dtype=np.int16)

        duration_sec = len(all_samples) / float(cfg.RATE)
        if duration_sec <= cfg.MIN_LENGTH_SEC:
            print("Mic recording too short.")
            self.short_recording = True
            self.recording_too_short.emit()
            return

        # Get next counter and form filename
        counter = get_next_counter("mic")
        filename = f"mic_{counter}.wav"
        filepath = os.path.join(cfg.OUTPUT_DIR, filename)
        os.makedirs(cfg.OUTPUT_DIR, exist_ok=True)
        try:
            with wave.open(filepath, 'wb') as wf:
                wf.setnchannels(cfg.CHANNELS)
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(cfg.RATE)
                wf.writeframes(all_samples.tobytes())
            print(f"Mic WAV saved: {filepath}")
            self.recording_saved.emit(filename)  # Emit the filename
        except Exception as e:
            print(f"Error saving mic WAV: {e}")

        self.soundlevel = 0.0

# Only define ADCRecorder if not on Windows
if not cfg.WINDOWS:
    class ADCRecorder(QObject):
        """
        Recorder that samples MCP3008.CH7 at cfg.ADC_RATE (e.g. 8000 Hz),
        packs 16-bit PCM, and writes a WAV file. Emits 'recording_too_short'
        if duration ≤ cfg.MIN_LENGTH_SEC, and 'recording_saved' with filename when saved.
        """
        recording_too_short = pyqtSignal()
        recording_saved = pyqtSignal(str)  # Emits filename of saved recording

        def __init__(self):
            super().__init__()
            self.recording = False
            self.frames = []  # List of numpy arrays (int16)
            self.short_recording = False
            self.soundlevel = 0.0
            self._read_thread = None
            self._stop_event = threading.Event()

            # UI timer
            self.timer = QTimer(self)
            self.timer.timeout.connect(self._update_ui)
            self.timer.start(50)

            # SPI setup for MCP3008
            self.spi = spidev.SpiDev()
            self.spi.open(0, 0)
            self.spi.max_speed_hz = 1350000

            self.ADC_MAX = 1023
            self.PCM_SCALE = 32767.0

        def _update_ui(self):
            pass

        def toggle_recording(self):
            if self.recording:
                self.stop()
            else:
                self.start()

        def start(self):
            """Launch the ADC-reader thread."""
            if self.recording:
                return

            self.frames = []
            self.short_recording = False
            self._stop_event.clear()
            self.recording = True

            self._read_thread = threading.Thread(target=self._read_loop, daemon=True)
            self._read_thread.start()
            print("ADC recording started.")

        def _read_loop(self):
            """
            Read cfg.ADC_CHUNK samples from MCP3008 at cfg.ADC_RATE.
            Convert to int16 PCM.
            """
            sample_interval = 1.0 / cfg.ADC_RATE
            channel = cfg.ADC_CHANNEL
            chunk_interval = cfg.ADC_CHUNK / float(cfg.ADC_RATE)

            while not self._stop_event.is_set():
                buf = np.zeros(cfg.ADC_CHUNK, dtype=np.int16)
                max_lvl = 0

                for i in range(cfg.ADC_CHUNK):
                    raw = self._read_adc(channel)
                    normalized = raw / float(self.ADC_MAX)
                    centered = normalized - 0.5
                    pcm_val = int(centered * self.PCM_SCALE)
                    buf[i] = pcm_val
                    lvl = abs(pcm_val)
                    if lvl > max_lvl:
                        max_lvl = lvl
                    time.sleep(sample_interval)
                    if self._stop_event.is_set():
                        break

                self.soundlevel = float(max_lvl)
                self.frames.append(buf.copy())

                if self._stop_event.is_set():
                    break

                elapsed = cfg.ADC_CHUNK * sample_interval
                if elapsed < chunk_interval:
                    time.sleep(chunk_interval - elapsed)

        def _read_adc(self, channel):
            """SPI transaction for MCP3008 single-ended read."""
            assert 0 <= channel <= 7
            tx = [1, (8 + channel) << 4, 0]
            resp = self.spi.xfer2(tx)
            raw = ((resp[1] & 0x03) << 8) | resp[2]
            return raw

        def stop(self):
            """Signal read-thread to end, concatenate, check length, write WAV."""
            if not self.recording:
                return

            self._stop_event.set()
            if self._read_thread is not None:
                self._read_thread.join()
                self._read_thread = None

            self.recording = False

            try:
                all_samples = np.concatenate(self.frames, axis=0)
            except ValueError:
                all_samples = np.zeros(0, dtype=np.int16)

            duration_sec = len(all_samples) / float(cfg.ADC_RATE)
            if duration_sec <= cfg.MIN_LENGTH_SEC:
                print("ADC recording too short.")
                self.short_recording = True
                self.recording_too_short.emit()
                return

            # Get next counter and form filename
            counter = get_next_counter("adc")
            filename = f"adc_{counter}.wav"
            filepath = os.path.join(cfg.OUTPUT_DIR, filename)
            os.makedirs(cfg.OUTPUT_DIR, exist_ok=True)

            try:
                with wave.open(filepath, 'wb') as wf:
                    wf.setnchannels(cfg.CHANNELS)
                    wf.setsampwidth(2)
                    wf.setframerate(cfg.ADC_RATE)
                    wf.writeframes(all_samples.tobytes())
                print(f"ADC WAV saved: {filepath}")
                self.recording_saved.emit(filename)  # Emit the filename
            except Exception as e:
                print(f"Error saving ADC WAV: {e}")

            self.soundlevel = 0.0
            self.spi.close()

else:
    class ADCRecorder(QObject):
        """
        Dummy ADCRecorder for Windows where spidev is unavailable.
        Emits recording_too_short immediately to inform user.
        """
        recording_too_short = pyqtSignal()
        recording_saved = pyqtSignal(str)  # Dummy signal for compatibility

        def __init__(self):
            super().__init__()
            self.recording = False
            self.short_recording = False
            self.soundlevel = 0.0
            self.timer = QTimer(self)
            self.timer.timeout.connect(self._update_ui)
            self.timer.start(50)

        def _update_ui(self):
            pass

        def toggle_recording(self):
            print("ADC recording not supported on Windows.")
            self.short_recording = True
            self.recording_too_short.emit()

        def start(self):
            self.toggle_recording()

        def stop(self):
            self.recording = False