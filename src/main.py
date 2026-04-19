import threading
import time
from datetime import datetime

from .audio import play_tone, play_wav, record_with_monitor
from .config import (
    GREETING_PATH,
    MAX_RECORDING_SECONDS,
    MIN_RECORDING_SECONDS,
    RECORDINGS_DIR,
)
from .hook import Hook


def run_session(hook: Hook) -> None:
    on_cradle = threading.Event()
    hook.on_cradle(on_cradle.set)
    try:
        print("[session] lifted")

        if not play_wav(GREETING_PATH, on_cradle):
            print("[session] hung up during greeting")
            return
        if not play_tone(on_cradle):
            print("[session] hung up during tone")
            return

        RECORDINGS_DIR.mkdir(parents=True, exist_ok=True)
        path = RECORDINGS_DIR / f"{datetime.now():%Y%m%d-%H%M%S}.wav"
        print(f"[session] recording to {path.name}")

        start = time.monotonic()
        record_with_monitor(path, on_cradle, MAX_RECORDING_SECONDS)
        duration = time.monotonic() - start

        if duration < MIN_RECORDING_SECONDS:
            path.unlink(missing_ok=True)
            print(f"[session] too short ({duration:.1f}s), discarded")
        else:
            print(f"[session] saved {path.name} ({duration:.1f}s)")
    finally:
        hook.clear_on_cradle()


def main() -> None:
    print("guest-phone: ready")
    hook = Hook()

    if hook.is_lifted:
        print("[boot] handset currently lifted, waiting for cradle")
        hook.wait_for_cradle()

    while True:
        print("[idle] waiting for lift")
        hook.wait_for_lift()
        try:
            run_session(hook)
        except Exception as e:
            print(f"[error] {e}")


if __name__ == "__main__":
    main()
