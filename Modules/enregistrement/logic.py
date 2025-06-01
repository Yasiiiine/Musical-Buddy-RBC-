# Modules/enregistrement/logic.py

import threading
import time
import wave
import os
import datetime

import numpy as np
import sounddevice as sd                   # for microphone capture
from PyQt5.QtCore import QObject, QTimer, pyqtSignal

import Modules.enregistrement.config as cfg

class MicRecorder(QObject):
    """
    Recorder that captures from the default system mic (via sounddevice)
    and writes a 16-bit WAV at cfg.RATE (e.g. 44100 Hz). Emits 'recording_too_short' 
    if total duration ≤ cfg.MIN_LENGTH_SEC.
    """
    recording_too_short = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.recording      = False
        self.frames         = []         # list of numpy arrays (int16) 
        self.short_recording = False
        self.soundlevel     = 0.0        # for UI meter
        self._stream        = None
        self._lock          = threading.Lock()

        # A Qt timer just to update UI (if you have a level-meter)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_ui)
        self.timer.start(50)  # every 50 ms

    def _update_ui(self):
        # In a real app, you’d signal your UI to repaint a level bar.
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

        # Open a sounddevice.InputStream
        self._stream = sd.InputStream(
            samplerate=cfg.RATE, 
            channels=1, 
            dtype='int16',
            blocksize=cfg.CHUNK,
            callback=self._audio_callback
        )
        self._stream.start()
        print("Mic recording started.")

    def _audio_callback(self, indata, frames, time_info, status):
        """
        This callback runs in sounddevice’s audio thread. 
        We simply append each incoming block to self.frames.
        """
        # indata is shape (cfg.CHUNK, 1), dtype=int16
        with self._lock:
            # Flatten to 1D and store
            self.frames.append(indata.copy().reshape(cfg.CHUNK))

            # Update a rough soundlevel (peak in this chunk)
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

        # How long is it?
        duration_sec = len(all_samples) / float(cfg.RATE)
        if duration_sec <= cfg.MIN_LENGTH_SEC:
            print("Mic recording too short.")
            self.short_recording = True
            self.recording_too_short.emit()
            return

        # Write WAV
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename  = f"mic_{timestamp}.wav"
        filepath  = os.path.join(cfg.OUTPUT_DIR, filename)
        os.makedirs(cfg.OUTPUT_DIR, exist_ok=True)
        try:
            with wave.open(filepath, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)         # 2 bytes = 16 bits
                wf.setframerate(cfg.RATE)
                wf.writeframes(all_samples.tobytes())
            print(f"Mic WAV saved: {filepath}")
        except Exception as e:
            print(f"Error saving mic WAV: {e}")

        # Reset soundlevel
        self.soundlevel = 0.0
# Modules/enregistrement/logic.py (continued)

import spidev   # for MCP3008 ADC access

class ADCRecorder(QObject):
    """
    Recorder that samples MCP3008.CH7 at cfg.ADC_RATE (e.g. 8000 Hz), 
    packs 16-bit PCM, and writes a WAV file. Emits 'recording_too_short' 
    if duration ≤ cfg.MIN_LENGTH_SEC.
    """
    recording_too_short = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.recording       = False
        self.frames          = []       # list of numpy arrays (int16)
        self.short_recording = False
        self.soundlevel      = 0.0
        self._read_thread    = None
        self._stop_event     = threading.Event()

        # UI timer (for a level-meter, if you want one)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_ui)
        self.timer.start(50)

        # SPI setup (MCP3008)
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)                 # bus=0, device=0
        self.spi.max_speed_hz = 1350000     # 1.35 MHz or lower

        self.ADC_MAX   = 1023               # MCP3008 is 10-bit
        self.PCM_SCALE = 32767.0            # to map to signed 16-bit

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
        Continuously read cfg.ADC_CH samples from MCP3008 at cfg.ADC_RATE 
        until stop() is called. Each CHUNK is converted to int16 PCM.
        """
        sample_interval = 1.0 / cfg.ADC_RATE      # e.g. 1/8000 s
        channel         = cfg.ADC_CHANNEL         # should be 7

        chunk_interval  = cfg.ADC_CHUNK / float(cfg.ADC_RATE)

        while not self._stop_event.is_set():
            buf     = np.zeros(cfg.ADC_CHUNK, dtype=np.int16)
            max_lvl = 0

            for i in range(cfg.ADC_CHUNK):
                raw = self._read_adc(channel)        # 0…1023

                # Normalize → [0…1], center → [–0.5…+0.5], scale → int16
                normalized = raw / float(self.ADC_MAX)
                centered   = normalized - 0.5
                pcm_val    = int(centered * self.PCM_SCALE)

                buf[i] = pcm_val
                lvl = abs(pcm_val)
                if lvl > max_lvl:
                    max_lvl = lvl

                # Sleep to maintain the desired sample rate
                time.sleep(sample_interval)
                if self._stop_event.is_set():
                    break

            # Update the UI meter
            self.soundlevel = float(max_lvl)

            # Store this chunk
            self.frames.append(buf.copy())

            if self._stop_event.is_set():
                break

            # If read+conversion took less than chunk_interval, pause
            elapsed = cfg.ADC_CHUNK * sample_interval
            if elapsed < chunk_interval:
                time.sleep(chunk_interval - elapsed)

        # Thread ends here; stop() will handle the rest.

    def _read_adc(self, channel):
        """
        SPI transaction for MCP3008 single-ended read on [0…7].
        Returns an int [0…1023].
        """
        assert 0 <= channel <= 7
        tx   = [1, (8 + channel) << 4, 0]
        resp = self.spi.xfer2(tx)
        raw  = ((resp[1] & 0x03) << 8) | resp[2]
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

        # Combine all chunks
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

        # Write WAV
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename  = f"adc_{timestamp}.wav"
        filepath  = os.path.join(cfg.OUTPUT_DIR, filename)
        os.makedirs(cfg.OUTPUT_DIR, exist_ok=True)

        try:
            with wave.open(filepath, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)               # 2 bytes = 16 bits PCM
                wf.setframerate(cfg.ADC_RATE)
                wf.writeframes(all_samples.tobytes())
            print(f"ADC WAV saved: {filepath}")
        except Exception as e:
            print(f"Error saving ADC WAV: {e}")

        self.soundlevel = 0.0
        self.spi.close()


import spidev


class ADCRecorder(QObject):
    """
    Continuously reads MCP3008 channel cfg.ADC_CHANNEL at cfg.ADC_RATE (Hz),
    converts each 10-bit reading into signed 16-bit PCM, and, upon stop(),
    writes exactly the captured samples to a WAV with sample rate = cfg.ADC_RATE.
    Emits recording_too_short if total duration <= cfg.MIN_LENGTH_SEC.
    """
    recording_too_short = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.recording       = False
        self.short_recording = False
        self.soundlevel      = 0.0         # peak level (for UI meter)
        self._stop_event     = threading.Event()
        self._read_thread    = None

        # Prepare SPI for MCP3008
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)                 # BUS=0, DEVICE=0 by default
        self.spi.max_speed_hz = 1350000     # 1.35 MHz is safe for MCP3008

        # Precompute constants:
        self.ADC_MAX   = 1023               # 10-bit MCP3008
        self.PCM_SCALE = 32767.0            # signed 16-bit full scale

        # A QTimer just to drive repaint (UI meter). We don't stop it here,
        # but it only matters if this widget is alive.
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._dummy_update)
        self.timer.start(50)                # 50 ms interval

    def _dummy_update(self):
        # No-op; this allows the UI to call update() so paintEvent gets triggered.
        pass

    def toggle_recording(self):
        """Start or stop recording based on current state."""
        if self.recording:
            self.stop()
        else:
            self.start()

    def start(self):
        """Begin the background thread that reads one ADC sample every 1/ADC_RATE seconds."""
        if self.recording:
            return

        self.recording       = True
        self.short_recording = False
        self.soundlevel      = 0.0
        self._stop_event.clear()

        # Launch a daemon thread so it won't block GUI exit
        self._read_thread = threading.Thread(target=self._read_loop, daemon=True)
        self._read_thread.start()
        print("ADC recording started.")

    def _read_loop(self):
        """
        This loop runs in a separate thread. It uses perf_counter() to schedule
        each sample precisely every (1 / cfg.ADC_RATE) seconds until stop_event is set.
        All PCM samples go into a Python list for minimal overhead. We also track
        the peak absolute value per sample so the UI meter can show a level.
        """
        channel = cfg.ADC_CHANNEL
        target_interval = 1.0 / cfg.ADC_RATE  # e.g. 0.000125 sec for 8000 Hz

        # We'll accumulate samples in a Python list, then cast to numpy once at the end
        pcm_list = []
        next_time = time.perf_counter()

        while not self._stop_event.is_set():
            now = time.perf_counter()
            if now < next_time:
                # Sleep only the remainder; checking repeatedly minimizes drift
                time.sleep(next_time - now)
                continue

            # Time to read a new sample:
            raw = self._read_adc(channel)    # int from 0..1023
            normalized = raw / float(self.ADC_MAX)   # 0.0..1.0
            centered   = normalized - 0.5            # –0.5..+0.5
            pcm_val    = int(centered * self.PCM_SCALE)  # –32767..+32767
            pcm_list.append(pcm_val)

            # Update peak for UI meter
            abs_val = abs(pcm_val)
            if abs_val > self.soundlevel:
                self.soundlevel = float(abs_val)

            # Schedule next sample time
            next_time += target_interval

            # Grab any “stop” request after producing this sample
            if self._stop_event.is_set():
                break

        # We only reach here when stop() is called; convert list→NumPy array:
        if pcm_list:
            all_samples = np.array(pcm_list, dtype=np.int16)
        else:
            all_samples = np.zeros(0, dtype=np.int16)

        # Compute actual duration
        duration_sec = len(all_samples) / float(cfg.ADC_RATE)
        if duration_sec <= cfg.MIN_LENGTH_SEC:
            print("ADC recording too short (%.2f s)" % duration_sec)
            self.short_recording = True
            self.recording_too_short.emit()
            # We still close SPI below, but do not write a file
            self.spi.close()
            self.recording = False
            return

        # Otherwise, write exactly the captured samples into a WAV:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename  = f"adc_{timestamp}.wav"
        filepath  = os.path.join(cfg.OUTPUT_DIR, filename)
        os.makedirs(cfg.OUTPUT_DIR, exist_ok=True)

        try:
            with wave.open(filepath, 'wb') as wf:
                wf.setnchannels(1)                   # mono
                wf.setsampwidth(2)                   # 2 bytes = 16 bit PCM
                wf.setframerate(cfg.ADC_RATE)        # 8000 Hz (or whatever you set)
                wf.writeframes(all_samples.tobytes())
            print(f"ADC WAV saved: {filepath} (duration {duration_sec:.2f}s)")
        except Exception as e:
            print("Error saving ADC WAV:", e)

        self.soundlevel = 0.0
        self.spi.close()
        self.recording = False

    def _read_adc(self, channel):
        """
        Low‐level SPI transaction for a single‐ended read on MCP3008 [0..7].
        Returns an integer 0..1023.
        """
        assert 0 <= channel <= 7
        tx   = [1, (8 + channel) << 4, 0]
        resp = self.spi.xfer2(tx)
        raw  = ((resp[1] & 0x03) << 8) | resp[2]
        return raw

    def stop(self):
        """
        Called when the user toggles “Stop Recording.” Signal the thread to end,
        then wait for it to finish so that _read_loop will write the file.
        """
        if not self.recording:
            return

        self._stop_event.set()
        if self._read_thread is not None:
            self._read_thread.join()
            self._read_thread = None

        # After join(), _read_loop has already closed SPI and possibly written the file.
        # We simply mark recording = False here if it wasn’t done already.
        self.recording = False
