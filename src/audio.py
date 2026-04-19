import queue
import threading
from pathlib import Path

import numpy as np
import sounddevice as sd
import soundfile as sf

from .config import (
    AUDIO_DEVICE_NAME,
    BLOCK_SIZE,
    MONITOR_GAIN,
    SAMPLE_RATE,
    TONE_AMPLITUDE,
    TONE_DURATION,
    TONE_FREQ,
)


def _device_index() -> int:
    for i, d in enumerate(sd.query_devices()):
        if AUDIO_DEVICE_NAME in d["name"]:
            return i
    raise RuntimeError(f"Audio device {AUDIO_DEVICE_NAME!r} not found")


def _play_until_done_or_cancelled(cancel: threading.Event) -> bool:
    try:
        while sd.get_stream().active:
            if cancel.wait(timeout=0.05):
                return False
        return True
    finally:
        sd.stop()


def play_wav(path: Path, cancel: threading.Event) -> bool:
    data, sr = sf.read(str(path), dtype="float32", always_2d=False)
    sd.play(data, samplerate=sr, device=_device_index())
    return _play_until_done_or_cancelled(cancel)


def play_tone(cancel: threading.Event) -> bool:
    t = np.arange(int(TONE_DURATION * SAMPLE_RATE)) / SAMPLE_RATE
    tone = (TONE_AMPLITUDE * np.sin(2 * np.pi * TONE_FREQ * t)).astype("float32")
    sd.play(tone, samplerate=SAMPLE_RATE, device=_device_index())
    return _play_until_done_or_cancelled(cancel)


def record_with_monitor(path: Path, stop: threading.Event, max_seconds: float) -> None:
    dev = _device_index()
    write_q: queue.Queue = queue.Queue()

    with sf.SoundFile(
        str(path), mode="w", samplerate=SAMPLE_RATE, channels=1, subtype="PCM_16"
    ) as f:
        def callback(indata, outdata, frames, time_info, status):
            write_q.put_nowait(indata.copy())
            mono_mix = indata[:, 0] * MONITOR_GAIN
            outdata[:, 0] = mono_mix
            outdata[:, 1] = mono_mix

        def writer():
            while True:
                block = write_q.get()
                if block is None:
                    return
                f.write(block)

        writer_thread = threading.Thread(target=writer, daemon=True)
        writer_thread.start()

        try:
            with sd.Stream(
                device=(dev, dev),
                channels=(1, 2),
                samplerate=SAMPLE_RATE,
                blocksize=BLOCK_SIZE,
                dtype="float32",
                callback=callback,
            ):
                stop.wait(timeout=max_seconds)
        finally:
            write_q.put(None)
            writer_thread.join(timeout=2.0)
