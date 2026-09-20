# vanta/timer.py

from __future__ import annotations

from datetime import datetime
from time import monotonic


class Timer:
    """A simple timer with start, stop, pause, and reset support."""

    def __init__(self, *, autostart: bool = False):
        self._start_time: datetime | None = None
        self._stop_time: datetime | None = None

        self._start_tick: float | None = None
        self._stop_tick: float | None = None

        self._pause_start: float | None = None
        self._paused_total: float = 0.0

        self._running = False
        self._paused = False

        if autostart:
            self.start()

    @property
    def elapsed(self) -> float:
        """Return elapsed active time in seconds."""
        if self._start_tick is None:
            return 0.0

        if self._running:
            current = monotonic()
        elif self._stop_tick is not None:
            current = self._stop_tick
        else:
            return 0.0

        elapsed = current - self._start_tick - self._paused_total

        if self._paused and self._pause_start is not None:
            elapsed -= current - self._pause_start

        return round(max(0.0, elapsed), 3)

    @property
    def ms(self) -> int:
        """Return elapsed active time in milliseconds."""
        return round(self.elapsed * 1000)

    @property
    def running(self) -> bool:
        """Return whether the timer is running."""
        return self._running

    @property
    def paused(self) -> bool:
        """Return whether the timer is paused."""
        return self._paused

    @property
    def start_time(self) -> datetime | None:
        """Return when the timer was started."""
        return self._start_time

    @property
    def stop_time(self) -> datetime | None:
        """Return when the timer was stopped."""
        return self._stop_time

    def start(self) -> Timer:
        """Start or resume the timer."""
        if self._running:
            return self

        now = monotonic()

        if self._start_tick is None:
            self._start_tick = now
            self._start_time = datetime.now()

        if self._paused:
            if self._pause_start is not None:
                self._paused_total += now - self._pause_start

            self._pause_start = None
            self._paused = False

        self._stop_tick = None
        self._stop_time = None
        self._running = True

        return self

    def stop(self) -> Timer:
        """Stop the timer and preserve its elapsed time."""
        if not self._running:
            return self

        now = monotonic()

        if self._paused:
            if self._pause_start is not None:
                self._paused_total += now - self._pause_start

            self._pause_start = None
            self._paused = False

        self._stop_tick = now
        self._stop_time = datetime.now()
        self._running = False

        return self

    def pause(self) -> Timer:
        """Pause the timer."""
        if not self._running or self._paused:
            return self

        self._pause_start = monotonic()
        self._paused = True

        return self

    def unpause(self) -> Timer:
        """Resume a paused timer."""
        if not self._running or not self._paused:
            return self

        now = monotonic()

        if self._pause_start is not None:
            self._paused_total += now - self._pause_start

        self._pause_start = None
        self._paused = False

        return self

    def reset(self) -> Timer:
        """Reset the timer to its initial state."""
        self._start_time = None
        self._stop_time = None

        self._start_tick = None
        self._stop_tick = None

        self._pause_start = None
        self._paused_total = 0.0

        self._running = False
        self._paused = False

        return self

    def __enter__(self) -> Timer:
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.stop()