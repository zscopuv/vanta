from __future__ import annotations

import sys
import time
from typing import TextIO


class Progress:
    """Render a simple progress bar in the terminal.

    Example:

        >>> progress = Progress(100, label="Downloading")
        >>> while not progress.finished:
        ...     do_something()
        ...     progress.update()

    Args:
        total: The total number of steps.
        label: Text displayed before the progress bar.
        width: Width of the progress bar.
        interactive: Whether to render progress updates.
        file: Output stream used for rendering.
    """

    def __init__(
        self,
        total: int,
        *,
        label: str = "",
        width: int = 30,
        interactive: bool = True,
        file: TextIO | None = None,
    ) -> None:
        if total <= 0:
            raise ValueError("Progress total must be greater than zero.")

        if width <= 0:
            raise ValueError("Progress width must be greater than zero.")

        self._total = int(total)
        self._label = str(label)
        self._width = int(width)
        self._interactive = bool(interactive)
        self._file = file if file is not None else sys.stdout

        self._current = 0
        self._started = False
        self._finished = False

        self._start_time: float | None = None
        self._finish_time: float | None = None

    @property
    def total(self) -> int:
        """Return the total number of steps."""
        return self._total

    @property
    def current(self) -> int:
        """Return the current progress."""
        return self._current

    @property
    def percentage(self) -> float:
        """Return progress as a percentage."""
        return (self._current / self._total) * 100

    @property
    def finished(self) -> bool:
        """Return whether the progress has finished."""
        return self._finished

    @property
    def running(self) -> bool:
        """Return whether the progress is currently running."""
        return self._started and not self._finished

    @property
    def completed(self) -> bool:
        """Return whether the progress has reached its total."""
        return self._current >= self._total

    @property
    def remaining(self) -> int:
        """Return the number of remaining steps."""
        return max(0, self._total - self._current)

    @property
    def elapsed(self) -> float:
        """Return elapsed time in seconds."""
        if self._start_time is None:
            return 0.0

        end = (
            self._finish_time
            if self._finish_time is not None
            else time.monotonic()
        )

        return end - self._start_time

    def start(self) -> Progress:
        """Start rendering progress."""
        if self._started:
            return self

        self._started = True
        self._finished = False
        self._start_time = time.monotonic()
        self._finish_time = None

        self._render()

        return self

    def update(self, amount: int = 1) -> Progress:
        """Advance progress by ``amount``.

        Progress is capped at ``total``.
        """
        if amount < 0:
            raise ValueError("Progress update amount cannot be negative.")

        if not self._started:
            self.start()

        if self._finished:
            return self

        self._current = min(
            self._total,
            self._current + amount,
        )

        self._render()

        if self._current >= self._total:
            self.finish()

        return self

    def finish(self) -> Progress:
        """Finish the progress and render the completed state."""
        if not self._started:
            self.start()

        if self._finished:
            return self

        self._current = self._total
        self._finished = True
        self._finish_time = time.monotonic()

        self._render()

        if self._interactive:
            self._file.write("\n")
            self._file.flush()

        return self

    def reset(self) -> Progress:
        """Reset progress to its initial state."""
        self._current = 0
        self._started = False
        self._finished = False
        self._start_time = None
        self._finish_time = None

        return self

    def __enter__(self) -> Progress:
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if exc_type is None:
            self.finish()

    def _render(self) -> None:
        if not self._interactive:
            return

        percentage = self.percentage

        filled = round(
            self._width * percentage / 100
        )
        empty = self._width - filled

        bar = "█" * filled + "░" * empty

        line = (
            f"{self._label + ' ' if self._label else ''}"
            f"[{bar}] "
            f"{percentage:6.2f}% "
            f"({self._current}/{self._total})"
        )

        elapsed = self.elapsed
        eta = self._eta()

        if elapsed > 0:
            line += f" {elapsed:.1f}s"

        if eta is not None:
            line += f" ETA {eta:.1f}s"

        # Return to the beginning, clear the existing line,
        # then write the new progress state.
        self._file.write(f"\r\033[2K{line}")
        self._file.flush()

    def _eta(self) -> float | None:
        if self._current <= 0:
            return None

        elapsed = self.elapsed

        if elapsed <= 0:
            return None

        rate = self._current / elapsed

        if rate <= 0:
            return None

        return self.remaining / rate