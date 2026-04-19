# Guest Phone - Wedding Message Recorder

A Raspberry Pi-based audio recorder that repurposes an antique phone for wedding guest messages.

## Overview

Guests pick up the vintage phone, hear a greeting and a short tone, and leave a message. When they hang up, the recording is saved.

## Hardware

- Raspberry Pi 4 Model B (2GB RAM), Raspberry Pi OS (Trixie, 64-bit, headless)
- Antique telephone with original earpiece and mouthpiece
- USB audio adapter (C-Media based): green (line out) → earpiece, pink (mic in) → mouthpiece
- Hook switch on GPIO 17 (normally closed — circuit closed when handset lifted, open when on cradle)
- Mouthpiece transducer: the original carbon transmitter underperformed on this adapter (needs DC bias current it doesn't get) and is being replaced with a small electret capsule

## How it works

1. Program boots and waits for the hook switch to close (handset lifted)
2. Plays `~/greeting.wav` through the earpiece
3. Plays a short tone
4. Records the guest while playing a low-level sidetone back through the earpiece so they hear themselves
5. On hang-up, saves to `~/recordings/YYYYMMDD-HHMMSS.wav` (or discards if under 2 seconds)

## Setup on the Pi

```bash
sudo apt-get install -y git libportaudio2
git clone https://github.com/dave-taylor-7654/guest-phone.git
cd guest-phone
python3 -m venv --system-site-packages .venv
.venv/bin/pip install -r requirements.txt
```

Place your greeting at `~/greeting.wav` (mono, any sample rate).

## USB audio mixer setup

Disable auto gain control and set a clean capture level, then persist:

```bash
amixer -c 3 sset 'Auto Gain Control' off
amixer -c 3 sset Mic Capture 0dB
sudo alsactl store
```

(Card number may differ — check with `aplay -l`.)

## Running

```bash
.venv/bin/python -m src.main
```

Tunables live in `src/config.py` (hook pin, audio device match, sample rate, monitor gain, tone settings, recording length limits).

## Layout

```
src/
  main.py     # state machine: idle → greeting → record → save
  hook.py     # GPIO 17 wrapper
  audio.py    # playback + record-with-sidetone
  config.py   # tunables
```

## License

TBD

## Author

Dave
