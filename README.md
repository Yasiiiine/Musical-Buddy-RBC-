# Musical Buddy

**Musical Buddy** is an interactive music assistant built on Raspberry Pi and PyQt5, designed to assist musicians with practice, performance, and creativity. It integrates a modular system with dynamic visual transitions and real-time audio interaction.

---

## Features

- **Metronome** module with visual pulse and tempo control.
- **Voice Recorder** with waveform animation and spacebar control.
- **Playback** of recorded or preloaded sounds.
- **Tuner** module (in progress): detects pitch and shows tuning accuracy using buffered audio input.
- **AI Recommendation System** (in development): analyzes played notes or MIDI input and suggests musical patterns or next notes based on ML models.
- **Dynamic Interface** with transition animations and customizable themes (light/dark, bootup visuals).
- **Settings Module**: Select audio input/output sources and UI themes.

---

## Project Structure

```bash
Musical Buddy/
├── Musical-Buddy-RBC/
│   ├── Assets/                   # UI assets and sound files
│   │   └── recordings/          # Recorded audio or visual assets
│   ├── Modules/                 # Core modules
│   │   ├── enregistrement/      # Recording module
│   │   ├── metronome/           # Metronome module
│   │   ├── Parametres/          # App settings and preferences
│   │   ├── transcripteurMIDI/   # MIDI analysis (future)
│   │   ├── tuner/               # Tuner logic and UI
│   │   ├── Template4-7/         # Placeholder templates
│   ├── app.py                   # Launch controller
│   ├── main.py                  # App startup logic
│   ├── config.py                # General config
│   ├── screens.py               # UI screen navigation
│   ├── requirements.txt         # Dependencies
│   └── README.md                # Project overview

