from __future__ import annotations

from datetime import datetime


class Time:
    """Simple formatted representation of the current local time."""

    def __init__(self, format: str = "%H:%M:%S") -> None:
        self.format = format

    def __str__(self) -> str:
        return datetime.now().strftime(self.format)

    def __repr__(self) -> str:
        return f"Time({self.format!r})"

    def __format__(self, spec: str) -> str:
        return str(self) if not spec else format(str(self), spec)

    def render(self) -> str:
        """Return the formatted current time."""
        return str(self)

    def refresh(self) -> str:
        """Return the current time using the configured format."""
        return datetime.now().strftime(self.format)