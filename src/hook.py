from gpiozero import Button

from .config import HOOK_PIN


class Hook:
    def __init__(self, pin: int = HOOK_PIN):
        self._button = Button(pin, pull_up=True, bounce_time=0.05)

    @property
    def is_lifted(self) -> bool:
        return self._button.is_pressed

    def wait_for_lift(self) -> None:
        self._button.wait_for_press()

    def wait_for_cradle(self) -> None:
        self._button.wait_for_release()

    def on_cradle(self, fn) -> None:
        self._button.when_released = fn

    def clear_on_cradle(self) -> None:
        self._button.when_released = None
