from __future__ import annotations

import os
import shutil
import subprocess
import sys
import traceback as traceback_module
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Iterable, Literal, TextIO, TypeVar

from colorama import Fore, init

from .metadata import __version__, __desc__


init(autoreset=True)


T = TypeVar("T")
Output = Callable[[str], T]
Input = Callable[[str], str]
StreamName = Literal["stdout", "stderr"]


def _read_input(prompt: str) -> str:
    """Read a line using whatever ``builtins.input`` is current."""
    return input(prompt)


@dataclass(frozen=True, slots=True)
class Variant:
    """Configuration for a console message variant."""

    text: str
    bracket: str
    stream: StreamName = "stdout"


VARIANTS: dict[str, Variant] = {
    "debug": Variant(
        Fore.LIGHTBLACK_EX,
        Fore.BLACK,
        "stdout",
    ),
    "success": Variant(
        Fore.LIGHTGREEN_EX,
        Fore.GREEN,
        "stdout",
    ),
    "info": Variant(
        Fore.LIGHTBLUE_EX,
        Fore.BLUE,
        "stdout",
    ),
    "notice": Variant(
        Fore.LIGHTCYAN_EX,
        Fore.CYAN,
        "stdout",
    ),
    "warning": Variant(
        Fore.LIGHTYELLOW_EX,
        Fore.YELLOW,
        "stderr",
    ),
    "error": Variant(
        Fore.LIGHTRED_EX,
        Fore.RED,
        "stderr",
    ),
    "critical": Variant(
        Fore.LIGHTRED_EX,
        Fore.RED,
        "stderr",
    ),
}


DEFAULT_YES = frozenset({
    "y",
    "1",
    "ok",
    "ye",
    "yes",
    "yep",
    "yy",
})

DEFAULT_NO = frozenset({
    "n",
    "0",
    "no",
    "nah",
    "nn",
})


# Lower values are more verbose.
LOG_LEVELS: dict[str, int] = {
    "debug": 10,
    "info": 20,
    "notice": 25,
    "success": 30,
    "warning": 40,
    "error": 50,
    "critical": 60,
}


class Console:
    """Small, configurable terminal console helper for Vanta."""

    def __init__(
        self,
        color: bool | None = None,
        cls: bool = False,
        *,
        stream: TextIO | None = None,
        stdout: TextIO | None = None,
        stderr: TextIO | None = None,
        input_fn: Input | None = None,
        interactive: bool | None = None,
        level: str = "info",
    ) -> None:
        """
        Args:
            color:
                Whether ANSI colors should be used.

                ``None`` means automatic detection.

                Automatic detection respects:
                - ``NO_COLOR``
                - ``FORCE_COLOR``
                - TTY capability

            cls:
                Whether to clear the terminal during initialization.
                Defaults to ``False`` to avoid surprising behavior.

            stream:
                Backwards-compatible shorthand for the primary output
                stream. Equivalent to ``stdout=stream``.

            stdout:
                Stream used for normal console output.

            stderr:
                Stream used for warnings, errors, and critical messages.

            input_fn:
                Function used to read user input. Injectable for testing.

                ``None`` means the builtin ``input`` is resolved at
                call time, so replacements installed later (readline
                wrappers, test doubles) are honored.

            interactive:
                Whether interactive input is available.

                ``None`` means automatic TTY detection.

            level:
                Minimum message level to display.

                Supported levels:
                ``debug``, ``info``, ``notice``, ``success``,
                ``warning``, ``error``, ``critical``.
        """
        if stream is not None:
            if stdout is not None:
                raise ValueError(
                    "stream and stdout cannot both be provided."
                )
            stdout = stream

        self._stdout = stdout if stdout is not None else sys.stdout
        self._stderr = stderr if stderr is not None else sys.stderr
        self._input = input_fn if input_fn is not None else _read_input

        self._interactive = (
            self._detect_interactive()
            if interactive is None
            else bool(interactive)
        )

        self._level = self._normalize_level(level)
        self._color = self._should_color(color)

        if cls:
            self.clear()

    # ------------------------------------------------------------------
    # Configuration / detection
    # ------------------------------------------------------------------

    def _detect_interactive(self) -> bool:
        """Return whether stdin appears to be interactive."""
        try:
            return bool(sys.stdin.isatty())
        except (AttributeError, OSError, ValueError):
            return False

    @staticmethod
    def _normalize_level(level: str) -> str:
        """Normalize and validate a log level."""
        normalized = str(level).strip().lower()

        if normalized not in LOG_LEVELS:
            valid = ", ".join(LOG_LEVELS)
            raise ValueError(
                f"Unknown console level {level!r}. "
                f"Expected one of: {valid}."
            )

        return normalized

    def _is_tty(self, stream: object) -> bool:
        """Return whether a stream appears to be a TTY."""
        try:
            return bool(stream.isatty())  # type: ignore[attr-defined]
        except (AttributeError, OSError, ValueError):
            return False

    def _should_color(self, color: bool | None) -> bool:
        """Determine whether ANSI colors should be emitted."""
        # NO_COLOR convention:
        # https://no-color.org/
        if "NO_COLOR" in os.environ:
            return False

        # FORCE_COLOR is useful in CI/piped environments.
        if "FORCE_COLOR" in os.environ:
            return True

        if color is False:
            return False

        if color is True:
            return self._is_tty(self._stdout)

        return self._is_tty(self._stdout)

    @property
    def color(self) -> bool:
        """Whether ANSI colors are currently enabled."""
        return self._color

    @property
    def interactive(self) -> bool:
        """Whether the console is operating interactively."""
        return self._interactive

    @property
    def level(self) -> str:
        """Return the current minimum log level."""
        return self._level

    @property
    def width(self) -> int:
        """Return the current terminal width."""
        try:
            return shutil.get_terminal_size(fallback=(80, 24)).columns
        except OSError:
            return 80

    # ------------------------------------------------------------------
    # Terminal operations
    # ------------------------------------------------------------------

    def clear(self) -> None:
        """Best-effort terminal clearing.

        Failure to clear the terminal is intentionally non-fatal.
        Clearing is only attempted when the console is interactive.
        """
        if not self._interactive:
            return

        # Windows.
        if os.name == "nt":
            command = shutil.which("cls")

            if command:
                try:
                    subprocess.run(
                        [command],
                        check=False,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                    return
                except (OSError, subprocess.SubprocessError):
                    pass

            # `cls` is normally a shell builtin.
            try:
                subprocess.run(
                    ["cmd", "/c", "cls"],
                    check=False,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except (OSError, subprocess.SubprocessError):
                pass

            return

        # Unix-like systems.
        command = shutil.which("clear")

        if command:
            try:
                subprocess.run(
                    [command],
                    check=False,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                return
            except (OSError, subprocess.SubprocessError):
                pass

        # Last resort: ANSI.
        if self._color:
            try:
                print(
                    "\033[2J\033[H",
                    end="",
                    file=self._stdout,
                )
            except (BrokenPipeError, OSError, ValueError):
                pass

    @staticmethod
    def _timestamp() -> str:
        """Return the current local time as HH:MM:SS."""
        return datetime.now().strftime("%H:%M:%S")

    # ------------------------------------------------------------------
    # Formatting
    # ------------------------------------------------------------------

    def _prefix(self, variant: str) -> str:
        """Build a colored or plain message prefix."""
        variant = variant.lower()

        if variant not in VARIANTS:
            variant = "info"

        config = VARIANTS[variant]
        name = variant.upper()

        if not self._color:
            return f"[{name}] "

        return (
            f"{config.bracket}["
            f"{config.text}{name}"
            f"{config.bracket}]"
            f"{config.text} "
        )

    def _timestamp_text(self) -> str:
        """Build the timestamp portion of a message."""
        timestamp = f"[{self._timestamp()}]"

        if self._color:
            return f"{Fore.LIGHTBLACK_EX}{timestamp}"

        return timestamp

    def _should_emit(self, variant: str) -> bool:
        """Return whether a message meets the configured log level."""
        variant = variant.lower()

        if variant not in LOG_LEVELS:
            variant = "info"

        return LOG_LEVELS[variant] >= LOG_LEVELS[self._level]

    def _stream_for(self, variant: str) -> TextIO:
        """Return the output stream for a message variant."""
        config = VARIANTS.get(variant.lower(), VARIANTS["info"])

        if config.stream == "stderr":
            return self._stderr

        return self._stdout

    def _print(
        self,
        variant: str | None,
        message: str,
    ) -> None:
        """Print a timestamped message."""
        if variant is not None and not self._should_emit(variant):
            return

        stream = (
            self._stdout
            if variant is None
            else self._stream_for(variant)
        )

        timestamp = self._timestamp_text()

        if variant is not None:
            output = (
                f"{timestamp} "
                f"{self._prefix(variant)}"
                f"{message}"
            )
        else:
            output = f"{timestamp} {message}"

        try:
            print(output, file=stream)
        except (BrokenPipeError, OSError, ValueError):
            # Useful for:
            #
            #     vanta | head
            #
            return

    # ------------------------------------------------------------------
    # Logging methods
    # ------------------------------------------------------------------

    def debug(self, message: str) -> None:
        """Print a debug message."""
        self._print("debug", message)

    def info(self, message: str) -> None:
        """Print an informational message."""
        self._print("info", message)

    def notice(self, message: str) -> None:
        """Print a notice message."""
        self._print("notice", message)

    def success(self, message: str) -> None:
        """Print a success message."""
        self._print("success", message)

    def warning(self, message: str) -> None:
        """Print a warning message to stderr."""
        self._print("warning", message)

    def error(self, message: str) -> None:
        """Print an error message to stderr."""
        self._print("error", message)

    def critical(self, message: str) -> None:
        """Print a critical error message to stderr."""
        self._print("critical", message)

    def raw(
        self,
        message: str,
        timestamp: bool = True,
    ) -> None:
        """Print an unclassified message."""
        if timestamp:
            self._print(None, message)
            return

        try:
            print(message, file=self._stdout)
        except (BrokenPipeError, OSError, ValueError):
            return

    # ------------------------------------------------------------------
    # Exceptions
    # ------------------------------------------------------------------

    def exception(
        self,
        exc: BaseException,
        *,
        traceback: bool = False,
        prefix: str | None = None,
    ) -> None:
        """
        Render an exception.

        Args:
            exc:
                Exception to display.

            traceback:
                If ``True``, print the full traceback.

            prefix:
                Optional text displayed before the exception message.
        """
        message = str(exc) or type(exc).__name__

        if prefix:
            message = f"{prefix}: {message}"

        self.error(message)

        if not traceback:
            return

        formatted = "".join(
            traceback_module.format_exception(
                type(exc),
                exc,
                exc.__traceback__,
            )
        )

        try:
            print(formatted.rstrip(), file=self._stderr)
        except (BrokenPipeError, OSError, ValueError):
            return

    # ------------------------------------------------------------------
    # Input
    # ------------------------------------------------------------------

    def _require_interactive(self) -> None:
        """Ensure interactive input is available."""
        if not self._interactive:
            raise RuntimeError(
                "Interactive input is unavailable. "
                "Run the console in interactive mode."
            )

    def ask(
        self,
        question: str,
        output: Output[T] = str,
        error_message: str | None = None,
        *,
        retry: int | None = None,
    ) -> T:
        """
        Ask for input and convert it using ``output``.

        Args:
            question:
                Prompt shown to the user.

            output:
                Conversion/validation function.

            error_message:
                Message shown after invalid input.

            retry:
                Maximum number of retries after the initial attempt.

                ``None`` means retry indefinitely.
                ``0`` means one attempt only.

        Raises:
            ValueError:
                If retry is negative or maximum attempts are exceeded.

            RuntimeError:
                If the console is non-interactive.

            EOFError:
                If stdin reaches EOF.

            KeyboardInterrupt:
                If the user interrupts input.
        """
        self._require_interactive()
        self._validate_retry(retry)

        attempts = 0

        while True:
            try:
                answer = self._input(f"{question} ").strip()
            except EOFError:
                self.error("Input ended unexpectedly.")
                raise
            except KeyboardInterrupt:
                self.raw("")
                raise

            try:
                return output(answer)
            except (ValueError, TypeError) as exc:
                attempts += 1

                output_name = getattr(
                    output,
                    "__name__",
                    type(output).__name__,
                )

                self.error(
                    error_message
                    if error_message is not None
                    else f"Invalid. Please use {output_name}."
                )

                if retry is not None and attempts > retry:
                    raise ValueError(
                        f"Maximum number of retries "
                        f"({retry}) exceeded."
                    ) from exc

    def confirm(
        self,
        question: str,
        error_message: str | None = None,
        default: bool = True,
        *,
        retry: int | None = None,
        alias_yes: Iterable[str] | None = None,
        alias_no: Iterable[str] | None = None,
    ) -> bool:
        """
        Ask a yes/no question.

        Args:
            question:
                Prompt shown to the user.

            error_message:
                Message shown for invalid input.

            default:
                Value returned when the user presses Enter.

            retry:
                Maximum number of retries after the initial attempt.

                ``None`` means retry indefinitely.
                ``0`` means one attempt only.

            alias_yes:
                Additional values accepted as yes.

            alias_no:
                Additional values accepted as no.
        """
        self._require_interactive()
        self._validate_retry(retry)

        yes = self._normalize_aliases(
            DEFAULT_YES,
            alias_yes,
        )
        no = self._normalize_aliases(
            DEFAULT_NO,
            alias_no,
        )

        options = "Y/n" if default else "y/N"
        attempts = 0

        while True:
            try:
                answer = self._input(
                    f"{question} [{options}] "
                ).strip().lower()
            except EOFError:
                self.error("Input ended unexpectedly.")
                raise
            except KeyboardInterrupt:
                self.raw("")
                raise

            if not answer:
                return default

            if answer in yes:
                return True

            if answer in no:
                return False

            attempts += 1

            self.error(
                error_message
                if error_message is not None
                else "Invalid. Please reply using 'yes' or 'no'."
            )

            if retry is not None and attempts > retry:
                raise ValueError(
                    f"Maximum number of retries "
                    f"({retry}) exceeded."
                )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize_aliases(
        defaults: Iterable[str],
        aliases: Iterable[str] | None,
    ) -> frozenset[str]:
        """Normalize and merge default and custom aliases."""
        values = {
            str(value).strip().lower()
            for value in defaults
            if str(value).strip()
        }

        if aliases is not None:
            values.update(
                str(alias).strip().lower()
                for alias in aliases
                if str(alias).strip()
            )

        return frozenset(values)

    @staticmethod
    def _validate_retry(retry: int | None) -> None:
        """Validate a retry configuration."""
        if retry is None:
            return

        if isinstance(retry, bool) or not isinstance(retry, int):
            raise TypeError("retry must be an integer or None.")

        if retry < 0:
            raise ValueError("retry must be >= 0.")

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def _testall(self) -> None:
        """Print every available message variant."""
        self.debug(f"Vanta {__version__}")
        self.info(f"Vanta {__version__}")
        self.notice(f"Vanta {__version__}")
        self.success(f"Vanta {__version__}")
        self.warning(f"Vanta {__version__}")
        self.error(f"Vanta {__version__}")
        self.critical(f"Vanta {__version__}")
        self.raw(f"Vanta {__version__}")
        self.raw(f"Vanta {__version__}", False)