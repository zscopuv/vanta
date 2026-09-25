"""Simple terminal panel rendering for Vanta."""

from __future__ import annotations

import sys
from typing import TextIO


class Panel:
    """Render content inside a terminal panel.

    Example:

        >>> panel = Panel(
        ...     "Starting server...",
        ...     "Loading configuration...",
        ...     "Server ready.",
        ...     title="Status",
        ... )
        >>> print(panel)
        ╭──────── Status ────────╮
        │ Starting server...    │
        │ Loading configuration... │
        │ Server ready.         │
        ╰───────────────────────╯
    """

    def __init__(
        self,
        *content: object,
        title: str | None = None,
        width: int | None = None,
        padding: int = 1,
        border: bool = True,
    ) -> None:
        if width is not None and width < 1:
            raise ValueError("Width must be at least 1.")

        if padding < 0:
            raise ValueError("Padding cannot be negative.")

        self._content = tuple(str(value) for value in content)
        self._title = None if title is None else str(title)
        self._width = width
        self._padding = padding
        self._border = bool(border)

    @property
    def content(self) -> tuple[str, ...]:
        """Return the panel content lines."""
        return self._content

    @property
    def title(self) -> str | None:
        """Return the panel title."""
        return self._title

    @property
    def width(self) -> int | None:
        """Return the configured panel width."""
        return self._width

    @property
    def padding(self) -> int:
        """Return the horizontal padding."""
        return self._padding

    @property
    def border(self) -> bool:
        """Return whether the panel has a border."""
        return self._border

    def set_content(self, *content: object) -> Panel:
        """Replace the panel content."""
        self._content = tuple(str(value) for value in content)
        return self

    def set_title(self, title: str | None) -> Panel:
        """Replace or remove the panel title."""
        self._title = None if title is None else str(title)
        return self

    def render(self) -> str:
        """Render the panel and return it as a string."""
        lines = list(self._content) or [""]

        if not self._border:
            return "\n".join(
                (" " * self._padding) + line
                for line in lines
            )

        content_width = max(
            len(line)
            for line in lines
        )

        width = self._resolve_width(content_width)
        inner_width = width - 2

        top = self._top(inner_width)
        bottom = "╰" + "─" * inner_width + "╯"

        rendered = [top]

        content_width = inner_width - (self._padding * 2)

        for line in lines:
            rendered.append(
                "│"
                + " " * self._padding
                + line.ljust(content_width)
                + " " * self._padding
                + "│"
            )

        rendered.append(bottom)

        return "\n".join(rendered)

    def print(self, *, file: TextIO | None = None) -> None:
        """Print the rendered panel."""
        if file is None:
            file = sys.stdout

        print(self.render(), file=file)

    def __str__(self) -> str:
        return self.render()

    def _resolve_width(self, content_width: int) -> int:
        minimum_width = content_width + (self._padding * 2)

        if self._title:
            minimum_width = max(
                minimum_width,
                len(self._title) + 4,
            )

        minimum_width += 2

        if self._width is None:
            return minimum_width

        return max(self._width, minimum_width)

    def _top(self, inner_width: int) -> str:
        if not self._title:
            return "╭" + "─" * inner_width + "╮"

        title = f" {self._title} "

        if len(title) >= inner_width:
            title = title[:inner_width]

            return (
                "╭"
                + title
                + "╮"
            )

        remaining = inner_width - len(title)
        left = remaining // 2
        right = remaining - left

        return (
            "╭"
            + "─" * left
            + title
            + "─" * right
            + "╮"
        )