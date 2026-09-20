"""Simple terminal table rendering for Vanta."""

from __future__ import annotations

from typing import Iterable, Sequence


class Table:
    """Render simple, readable tables in the terminal.

    Example:
        >>> table = Table("Name", "Age", "Status")
        >>> table.add_row("Alice", 17, "Online")
        >>> table.add_row("Bob", 21, "Offline")
        >>> print(table)
        ┌───────┬─────┬─────────┐
        │ Name  │ Age │ Status  │
        ├───────┼─────┼─────────┤
        │ Alice │ 17  │ Online  │
        │ Bob   │ 21  │ Offline │
        └───────┴─────┴─────────┘
    """

    def __init__(
        self,
        *columns: str,
        align: str | Sequence[str] = "left",
        border: bool = True,
        header: bool = True,
    ) -> None:
        if not columns:
            raise ValueError("Table requires at least one column.")

        if any(not str(column).strip() for column in columns):
            raise ValueError("Column names cannot be empty.")

        self._columns = tuple(str(column) for column in columns)
        self._alignments = self._normalize_alignments(
            align,
            len(columns),
        )
        self._border = bool(border)
        self._header = bool(header)
        self._rows: list[tuple[str, ...]] = []

    @property
    def columns(self) -> tuple[str, ...]:
        """Return the table column names."""
        return self._columns

    @property
    def rows(self) -> tuple[tuple[str, ...], ...]:
        """Return the current rows."""
        return tuple(self._rows)

    def add_row(self, *values: object) -> Table:
        """Add one row and return the table for chaining."""
        if len(values) != len(self._columns):
            raise ValueError(
                f"Expected {len(self._columns)} values, "
                f"got {len(values)}."
            )

        self._rows.append(
            tuple(self._stringify(value) for value in values)
        )

        return self

    def add_rows(
        self,
        rows: Iterable[Iterable[object]],
    ) -> Table:
        """Add multiple rows and return the table."""
        for row in rows:
            self.add_row(*row)

        return self

    def clear(self) -> Table:
        """Remove all rows and return the table."""
        self._rows.clear()
        return self

    def render(self) -> str:
        """Render the table and return it as a string."""
        widths = self._widths()
        lines: list[str] = []

        if self._border:
            lines.append(
                self._horizontal(
                    widths,
                    "┌",
                    "┬",
                    "┐",
                )
            )

        if self._header:
            lines.append(self._row(self._columns, widths))

            if self._border:
                lines.append(
                    self._horizontal(
                        widths,
                        "├",
                        "┼",
                        "┤",
                    )
                )
            else:
                lines.append(self._separator(widths))

        for row in self._rows:
            lines.append(self._row(row, widths))

        if self._border:
            lines.append(
                self._horizontal(
                    widths,
                    "└",
                    "┴",
                    "┘",
                )
            )

        return "\n".join(lines)

    def print(self, *, file=None) -> None:
        """Print the rendered table."""
        import sys

        if file is None:
            file = sys.stdout

        print(self.render(), file=file)

    def __str__(self) -> str:
        return self.render()

    @staticmethod
    def _stringify(value: object) -> str:
        return "" if value is None else str(value)

    @staticmethod
    def _normalize_alignments(
        align: str | Sequence[str],
        count: int,
    ) -> tuple[str, ...]:
        if isinstance(align, str):
            alignments = [align] * count
        else:
            alignments = list(align)

            if len(alignments) != count:
                raise ValueError(
                    f"Expected {count} alignments, "
                    f"got {len(alignments)}."
                )

        normalized = tuple(
            str(value).lower()
            for value in alignments
        )

        invalid = set(normalized) - {
            "left",
            "center",
            "right",
        }

        if invalid:
            values = ", ".join(sorted(invalid))

            raise ValueError(
                f"Invalid alignment(s): {values}. "
                "Expected 'left', 'center', or 'right'."
            )

        return normalized

    def _widths(self) -> list[int]:
        rows = (
            self._rows
            if self._rows
            else [tuple("" for _ in self._columns)]
        )

        return [
            max(
                len(self._columns[index]),
                *(len(row[index]) for row in rows),
            )
            for index in range(len(self._columns))
        ]

    def _row(
        self,
        values: Sequence[str],
        widths: Sequence[int],
    ) -> str:
        cells = [
            self._align(
                value,
                width,
                self._alignments[index],
            )
            for index, (value, width)
            in enumerate(zip(values, widths))
        ]

        if self._border:
            return "│ " + " │ ".join(cells) + " │"

        return "  ".join(cells)

    @staticmethod
    def _align(
        value: str,
        width: int,
        alignment: str,
    ) -> str:
        if alignment == "right":
            return value.rjust(width)

        if alignment == "center":
            return value.center(width)

        return value.ljust(width)

    @staticmethod
    def _horizontal(
        widths: Sequence[int],
        left: str,
        middle: str,
        right: str,
    ) -> str:
        return (
            left
            + middle.join(
                "─" * (width + 2)
                for width in widths
            )
            + right
        )

    @staticmethod
    def _separator(
        widths: Sequence[int],
    ) -> str:
        return "  ".join(
            "─" * width
            for width in widths
        )