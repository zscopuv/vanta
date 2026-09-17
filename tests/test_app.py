from __future__ import annotations

import sys
from io import StringIO
from unittest.mock import Mock

import pytest

from vanta.app import Console, DEFAULT_NO, DEFAULT_YES


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class FakeStream(StringIO):
    def __init__(self, *, tty: bool = False) -> None:
        super().__init__()
        self.tty = tty

    def isatty(self) -> bool:
        return self.tty


@pytest.fixture(autouse=True)
def tty_stdin(monkeypatch: pytest.MonkeyPatch) -> None:
    """Give every test a stdin that looks like a terminal.

    Under pytest, stdin is replaced by a non-TTY capture object, so
    ``Console`` would auto-detect non-interactive mode and every
    ``ask``/``confirm``/``clear`` test would raise or no-op. Tests that
    care about the non-interactive path pass ``interactive=False``
    explicitly.
    """
    monkeypatch.setattr(sys, "stdin", FakeStream(tty=True))


# ---------------------------------------------------------------------------
# Construction / color detection
# ---------------------------------------------------------------------------


def test_color_is_disabled_for_non_tty_by_default() -> None:
    stream = FakeStream(tty=False)

    console = Console(cls=False, stream=stream)

    assert console._color is False


def test_color_is_enabled_for_tty_by_default() -> None:
    stream = FakeStream(tty=True)

    console = Console(cls=False, stream=stream)

    assert console._color is True


def test_color_false_disables_color_even_on_tty() -> None:
    stream = FakeStream(tty=True)

    console = Console(
        color=False,
        cls=False,
        stream=stream,
    )

    assert console._color is False


def test_color_true_does_not_force_ansi_into_non_tty() -> None:
    stream = FakeStream(tty=False)

    console = Console(
        color=True,
        cls=False,
        stream=stream,
    )

    assert console._color is False


def test_invalid_tty_stream_is_treated_as_non_tty() -> None:
    stream = Mock()
    stream.isatty.side_effect = OSError

    console = Console(cls=False, stream=stream)

    assert console._color is False


# ---------------------------------------------------------------------------
# Prefixes
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "variant",
    [
        "debug",
        "success",
        "info",
        "notice",
        "warning",
        "error",
        "critical",
    ],
)
def test_prefix_contains_variant_name(variant: str) -> None:
    console = Console(
        color=False,
        cls=False,
    )

    assert console._prefix(variant) == f"[{variant.upper()}] "


def test_prefix_falls_back_to_info_for_unknown_variant() -> None:
    console = Console(
        color=False,
        cls=False,
    )

    assert console._prefix("does-not-exist") == "[INFO] "


def test_prefix_is_case_insensitive() -> None:
    console = Console(
        color=False,
        cls=False,
    )

    assert console._prefix("SUCCESS") == "[SUCCESS] "


# ---------------------------------------------------------------------------
# Printing / streams
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "method, variant",
    [
        ("debug", "DEBUG"),
        ("info", "INFO"),
        ("success", "SUCCESS"),
        ("notice", "NOTICE"),
    ],
)
def test_message_methods_write_to_stdout(
    method: str,
    variant: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    stream = FakeStream()

    console = Console(
        color=False,
        cls=False,
        stream=stream,
        level="debug",
    )

    monkeypatch.setattr(
        console,
        "_timestamp",
        lambda: "12:34:56",
    )

    getattr(console, method)("hello")

    assert stream.getvalue() == (
        f"[12:34:56] [{variant}] hello\n"
    )


@pytest.mark.parametrize(
    "method, variant",
    [
        ("warning", "WARNING"),
        ("error", "ERROR"),
        ("critical", "CRITICAL"),
    ],
)
def test_message_methods_write_to_stderr(
    method: str,
    variant: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    stdout = FakeStream()
    stderr = FakeStream()

    console = Console(
        color=False,
        cls=False,
        stdout=stdout,
        stderr=stderr,
    )

    monkeypatch.setattr(
        console,
        "_timestamp",
        lambda: "12:34:56",
    )

    getattr(console, method)("hello")

    assert stdout.getvalue() == ""
    assert stderr.getvalue() == (
        f"[12:34:56] [{variant}] hello\n"
    )


def test_raw_uses_stdout() -> None:
    stdout = FakeStream()

    console = Console(
        color=False,
        cls=False,
        stdout=stdout,
    )

    console._timestamp = lambda: "12:34:56"

    console.raw("hello")

    assert stdout.getvalue() == "[12:34:56] hello\n"


def test_raw_without_timestamp() -> None:
    stdout = FakeStream()

    console = Console(
        color=False,
        cls=False,
        stdout=stdout,
    )

    console.raw(
        "hello",
        timestamp=False,
    )

    assert stdout.getvalue() == "hello\n"


def test_stream_alias_points_to_stdout() -> None:
    stream = FakeStream()

    console = Console(
        color=False,
        cls=False,
        stream=stream,
    )

    console.info("hello")

    assert stream.getvalue().endswith("[INFO] hello\n")


# ---------------------------------------------------------------------------
# Log levels
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "level, method, should_print",
    [
        ("debug", "debug", True),
        ("debug", "info", True),
        ("info", "debug", False),
        ("info", "info", True),
        ("notice", "info", False),
        ("notice", "notice", True),
        ("warning", "notice", False),
        ("warning", "warning", True),
        ("error", "warning", False),
        ("error", "error", True),
        ("critical", "error", False),
        ("critical", "critical", True),
    ],
)
def test_log_level_filtering(
    level: str,
    method: str,
    should_print: bool,
) -> None:
    stream = FakeStream()

    console = Console(
        color=False,
        cls=False,
        stdout=stream,
        stderr=stream,
        level=level,
    )

    getattr(console, method)("hello")

    if should_print:
        assert "hello" in stream.getvalue()
    else:
        assert stream.getvalue() == ""


def test_debug_is_filtered_by_default() -> None:
    stream = FakeStream()

    console = Console(
        color=False,
        cls=False,
        stream=stream,
    )

    console.debug("hidden")

    assert stream.getvalue() == ""


# ---------------------------------------------------------------------------
# ask()
# ---------------------------------------------------------------------------


def test_ask_returns_converted_value(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    console = Console(
        color=False,
        cls=False,
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda _: "123",
    )

    assert console.ask("Number:", int) == 123


def test_ask_retries_after_invalid_input(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    console = Console(
        color=False,
        cls=False,
    )

    answers = iter(["abc", "42"])

    monkeypatch.setattr(
        "builtins.input",
        lambda _: next(answers),
    )

    assert console.ask("Number:", int) == 42


def test_ask_respects_retry_limit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    console = Console(
        color=False,
        cls=False,
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda _: "abc",
    )

    with pytest.raises(
        ValueError,
        match="Maximum number of retries",
    ):
        console.ask(
            "Number:",
            int,
            retry=3,
        )


def test_ask_retry_zero_allows_a_single_attempt(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    attempts = 0

    def fake_input(_: str) -> str:
        nonlocal attempts
        attempts += 1
        return "bad"

    console = Console(
        color=False,
        cls=False,
    )

    monkeypatch.setattr(
        "builtins.input",
        fake_input,
    )

    with pytest.raises(
        ValueError,
        match="Maximum number of retries",
    ):
        console.ask(
            "Number:",
            int,
            retry=0,
        )

    assert attempts == 1


def test_ask_retry_none_retries_indefinitely(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    console = Console(
        color=False,
        cls=False,
    )

    answers = iter(["bad", "bad", "bad", "42"])

    monkeypatch.setattr(
        "builtins.input",
        lambda _: next(answers),
    )

    assert console.ask(
        "Number:",
        int,
        retry=None,
    ) == 42


def test_ask_custom_error_message(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    stderr = FakeStream()

    console = Console(
        color=False,
        cls=False,
        stderr=stderr,
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda _: "bad",
    )

    with pytest.raises(ValueError):
        console.ask(
            "Number:",
            int,
            error_message="Not a number.",
            retry=1,
        )

    assert "Not a number." in stderr.getvalue()


def test_ask_handles_eof(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    console = Console(
        color=False,
        cls=False,
    )

    def raise_eof(_: str) -> str:
        raise EOFError

    monkeypatch.setattr(
        "builtins.input",
        raise_eof,
    )

    with pytest.raises(EOFError):
        console.ask("Input:")


def test_ask_handles_keyboard_interrupt(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    console = Console(
        color=False,
        cls=False,
    )

    def raise_interrupt(_: str) -> str:
        raise KeyboardInterrupt

    monkeypatch.setattr(
        "builtins.input",
        raise_interrupt,
    )

    with pytest.raises(KeyboardInterrupt):
        console.ask("Input:")


# ---------------------------------------------------------------------------
# confirm()
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "answer, expected",
    [
        ("y", True),
        ("Y", True),
        ("yes", True),
        ("YES", True),
        ("1", True),
        ("ok", True),
        ("ye", True),
        ("yep", True),
        ("yy", True),
        ("n", False),
        ("N", False),
        ("no", False),
        ("0", False),
        ("nah", False),
        ("nn", False),
    ],
)
def test_confirm_default_aliases(
    monkeypatch: pytest.MonkeyPatch,
    answer: str,
    expected: bool,
) -> None:
    console = Console(
        color=False,
        cls=False,
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda _: answer,
    )

    assert console.confirm("Continue?") is expected


def test_confirm_default_true(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    console = Console(
        color=False,
        cls=False,
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda _: "",
    )

    assert console.confirm(
        "Continue?",
        default=True,
    ) is True


def test_confirm_default_false(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    console = Console(
        color=False,
        cls=False,
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda _: "",
    )

    assert console.confirm(
        "Continue?",
        default=False,
    ) is False


def test_confirm_custom_yes_aliases(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    console = Console(
        color=False,
        cls=False,
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda _: "yeah",
    )

    assert console.confirm(
        "Continue?",
        alias_yes=["yeah"],
    ) is True


def test_confirm_custom_no_aliases(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    console = Console(
        color=False,
        cls=False,
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda _: "nope",
    )

    assert console.confirm(
        "Continue?",
        alias_no=["nope"],
    ) is False


def test_confirm_aliases_are_case_insensitive(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    console = Console(
        color=False,
        cls=False,
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda _: "YUH",
    )

    assert console.confirm(
        "Continue?",
        alias_yes=["yuh"],
    ) is True


def test_confirm_aliases_ignore_empty_values(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    console = Console(
        color=False,
        cls=False,
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda _: "yeah",
    )

    assert console.confirm(
        "Continue?",
        alias_yes=["", "  ", "yeah"],
    ) is True


def test_confirm_retries_invalid_input(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    console = Console(
        color=False,
        cls=False,
    )

    answers = iter(["maybe", "yes"])

    monkeypatch.setattr(
        "builtins.input",
        lambda _: next(answers),
    )

    assert console.confirm("Continue?") is True


def test_confirm_respects_retry_limit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    console = Console(
        color=False,
        cls=False,
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda _: "maybe",
    )

    with pytest.raises(
        ValueError,
        match="Maximum number of retries",
    ):
        console.confirm(
            "Continue?",
            retry=3,
        )


def test_confirm_retry_zero_allows_a_single_attempt(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    attempts = 0

    def fake_input(_: str) -> str:
        nonlocal attempts
        attempts += 1
        return "maybe"

    console = Console(
        color=False,
        cls=False,
    )

    monkeypatch.setattr(
        "builtins.input",
        fake_input,
    )

    with pytest.raises(
        ValueError,
        match="Maximum number of retries",
    ):
        console.confirm(
            "Continue?",
            retry=0,
        )

    assert attempts == 1


def test_confirm_retry_none_retries_indefinitely(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    console = Console(
        color=False,
        cls=False,
    )

    answers = iter(["maybe", "wat", "nope", "yes"])

    monkeypatch.setattr(
        "builtins.input",
        lambda _: next(answers),
    )

    assert console.confirm(
        "Continue?",
        retry=None,
    ) is True


def test_confirm_custom_error_message(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    stderr = FakeStream()

    console = Console(
        color=False,
        cls=False,
        stderr=stderr,
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda _: "maybe",
    )

    with pytest.raises(ValueError):
        console.confirm(
            "Continue?",
            error_message="Please enter Y or N.",
            retry=1,
        )

    assert "Please enter Y or N." in stderr.getvalue()


def test_confirm_handles_eof(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    console = Console(
        color=False,
        cls=False,
    )

    def raise_eof(_: str) -> str:
        raise EOFError

    monkeypatch.setattr(
        "builtins.input",
        raise_eof,
    )

    with pytest.raises(EOFError):
        console.confirm("Continue?")


def test_confirm_handles_keyboard_interrupt(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    console = Console(
        color=False,
        cls=False,
    )

    def raise_interrupt(_: str) -> str:
        raise KeyboardInterrupt

    monkeypatch.setattr(
        "builtins.input",
        raise_interrupt,
    )

    with pytest.raises(KeyboardInterrupt):
        console.confirm("Continue?")


# ---------------------------------------------------------------------------
# Retry validation
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("retry", [-1, -10])
def test_negative_retry_is_rejected(retry: int) -> None:
    console = Console(
        color=False,
        cls=False,
    )

    with pytest.raises(
        ValueError,
        match="retry must be >= 0",
    ):
        console.ask(
            "Input:",
            retry=retry,
        )


@pytest.mark.parametrize(
    "retry",
    [True, False, 1.5, "3", 3.0, [], object()],
)
def test_invalid_retry_type_is_rejected(
    retry: object,
) -> None:
    console = Console(
        color=False,
        cls=False,
    )

    with pytest.raises(
        TypeError,
        match="retry must be an integer",
    ):
        console.ask(
            "Input:",
            retry=retry,  # type: ignore[arg-type]
        )


# ---------------------------------------------------------------------------
# Alias normalization
# ---------------------------------------------------------------------------


def test_default_aliases_are_present() -> None:
    assert "yes" in DEFAULT_YES
    assert "y" in DEFAULT_YES

    assert "no" in DEFAULT_NO
    assert "n" in DEFAULT_NO


def test_aliases_do_not_modify_defaults() -> None:
    aliases = ["custom"]

    normalized = Console._normalize_aliases(
        DEFAULT_YES,
        aliases,
    )

    assert "custom" in normalized
    assert "custom" not in DEFAULT_YES


def test_aliases_accept_non_string_values() -> None:
    normalized = Console._normalize_aliases(
        DEFAULT_YES,
        [123, "yeah"],
    )

    assert "123" in normalized
    assert "yeah" in normalized


# ---------------------------------------------------------------------------
# Interactive mode
# ---------------------------------------------------------------------------


def test_interactive_is_enabled_by_default() -> None:
    console = Console(
        color=False,
        cls=False,
    )

    assert console._interactive is True


def test_interactive_can_be_enabled() -> None:
    console = Console(
        color=False,
        cls=False,
        interactive=True,
    )

    assert console._interactive is True


def test_interactive_can_be_disabled() -> None:
    console = Console(
        color=False,
        cls=False,
        interactive=False,
    )

    assert console._interactive is False


def test_non_interactive_ask_raises() -> None:
    console = Console(
        color=False,
        cls=False,
        interactive=False,
    )

    with pytest.raises(
        RuntimeError,
        match="Interactive input is unavailable",
    ):
        console.ask("Input:")


def test_non_interactive_confirm_raises() -> None:
    console = Console(
        color=False,
        cls=False,
        interactive=False,
    )

    with pytest.raises(
        RuntimeError,
        match="Interactive input is unavailable",
    ):
        console.confirm("Continue?")


# ---------------------------------------------------------------------------
# Input function injection
# ---------------------------------------------------------------------------


def test_custom_input_function_is_used() -> None:
    calls: list[str] = []

    def fake_input(prompt: str) -> str:
        calls.append(prompt)
        return "123"

    console = Console(
        color=False,
        cls=False,
        input_fn=fake_input,
    )

    assert console.ask("Number:", int) == 123
    assert calls


def test_custom_input_function_works_with_confirm() -> None:
    def fake_input(_: str) -> str:
        return "yes"

    console = Console(
        color=False,
        cls=False,
        input_fn=fake_input,
    )

    assert console.confirm("Continue?") is True


# ---------------------------------------------------------------------------
# clear()
# ---------------------------------------------------------------------------


def test_clear_uses_clear_command_when_available(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    console = Console(
        color=False,
        cls=False,
    )

    monkeypatch.setattr(
        "vanta.app.os.name",
        "posix",
    )

    monkeypatch.setattr(
        "vanta.app.shutil.which",
        lambda command: (
            "/usr/bin/clear"
            if command == "clear"
            else None
        ),
    )

    run = Mock()

    monkeypatch.setattr(
        "vanta.app.subprocess.run",
        run,
    )

    console.clear()

    run.assert_called_once()


def test_clear_does_not_fail_when_command_is_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    console = Console(
        color=False,
        cls=False,
    )

    monkeypatch.setattr(
        "vanta.app.os.name",
        "posix",
    )

    monkeypatch.setattr(
        "vanta.app.shutil.which",
        lambda _: None,
    )

    console.clear()


def test_clear_ignores_subprocess_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    console = Console(
        color=False,
        cls=False,
    )

    monkeypatch.setattr(
        "vanta.app.os.name",
        "posix",
    )

    monkeypatch.setattr(
        "vanta.app.shutil.which",
        lambda _: "/usr/bin/clear",
    )

    monkeypatch.setattr(
        "vanta.app.subprocess.run",
        Mock(side_effect=OSError),
    )

    console.clear()


def test_constructor_clears_when_cls_enabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clear = Mock()

    monkeypatch.setattr(
        Console,
        "clear",
        clear,
    )

    Console(cls=True)

    clear.assert_called_once()


def test_constructor_does_not_clear_when_cls_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clear = Mock()

    monkeypatch.setattr(
        Console,
        "clear",
        clear,
    )

    Console(cls=False)

    clear.assert_not_called()


# ---------------------------------------------------------------------------
# Terminal width
# ---------------------------------------------------------------------------


def test_width_returns_positive_integer() -> None:
    console = Console(
        color=False,
        cls=False,
    )

    assert isinstance(console.width, int)
    assert console.width > 0


# ---------------------------------------------------------------------------
# Broken pipe handling
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "method",
    [
        "debug",
        "info",
        "success",
        "notice",
    ],
)
def test_stdout_methods_ignore_broken_pipe(
    method: str,
) -> None:
    stream = Mock()
    stream.isatty.return_value = False
    stream.write.side_effect = BrokenPipeError

    console = Console(
        color=False,
        cls=False,
        stream=stream,
    )

    getattr(console, method)("hello")


@pytest.mark.parametrize(
    "method",
    [
        "warning",
        "error",
        "critical",
    ],
)
def test_stderr_methods_ignore_broken_pipe(
    method: str,
) -> None:
    stderr = Mock()
    stderr.isatty.return_value = False
    stderr.write.side_effect = BrokenPipeError

    console = Console(
        color=False,
        cls=False,
        stderr=stderr,
    )

    getattr(console, method)("hello")


def test_raw_without_timestamp_ignores_broken_pipe() -> None:
    stream = Mock()
    stream.isatty.return_value = False
    stream.write.side_effect = BrokenPipeError

    console = Console(
        color=False,
        cls=False,
        stream=stream,
    )

    console.raw(
        "hello",
        timestamp=False,
    )


# ---------------------------------------------------------------------------
# Colored output
# ---------------------------------------------------------------------------


def test_colored_output_on_tty(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    stream = FakeStream(tty=True)

    console = Console(
        cls=False,
        stream=stream,
    )

    monkeypatch.setattr(
        console,
        "_timestamp",
        lambda: "12:34:56",
    )

    console.success("hello")

    output = stream.getvalue()

    assert "\x1b[" in output
    assert "SUCCESS" in output
    assert "hello" in output


def test_no_color_environment_disables_color(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("NO_COLOR", "1")

    stream = FakeStream(tty=True)

    console = Console(
        cls=False,
        stream=stream,
    )

    assert console._color is False


def test_force_color_enables_color(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("FORCE_COLOR", "1")

    stream = FakeStream(tty=True)

    console = Console(
        cls=False,
        stream=stream,
    )

    assert console._color is True


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


def test_exception_prints_exception_message() -> None:
    stderr = FakeStream()

    console = Console(
        color=False,
        cls=False,
        stderr=stderr,
    )

    console.exception(ValueError("something failed"))

    output = stderr.getvalue()

    assert "something failed" in output


def test_exception_supports_custom_prefix() -> None:
    stderr = FakeStream()

    console = Console(
        color=False,
        cls=False,
        stderr=stderr,
    )

    console.exception(
        RuntimeError("boom"),
        prefix="Failed",
    )

    output = stderr.getvalue()

    assert "Failed: boom" in output


def test_exception_falls_back_to_type_name() -> None:
    stderr = FakeStream()

    console = Console(
        color=False,
        cls=False,
        stderr=stderr,
    )

    console.exception(ValueError())

    assert "ValueError" in stderr.getvalue()


def test_exception_without_traceback_does_not_print_traceback() -> None:
    stderr = FakeStream()

    console = Console(
        color=False,
        cls=False,
        stderr=stderr,
    )

    console.exception(
        ValueError("boom"),
        traceback=False,
    )

    output = stderr.getvalue()

    assert "Traceback" not in output
    assert "boom" in output


def test_exception_with_traceback_prints_traceback() -> None:
    stderr = FakeStream()

    console = Console(
        color=False,
        cls=False,
        stderr=stderr,
    )

    try:
        raise ValueError("boom")
    except ValueError as exc:
        console.exception(
            exc,
            traceback=True,
        )

    output = stderr.getvalue()

    assert "Traceback" in output
    assert "ValueError" in output
    assert "boom" in output


# ---------------------------------------------------------------------------
# Custom streams
# ---------------------------------------------------------------------------


def test_stdout_and_stderr_can_be_configured_independently() -> None:
    stdout = FakeStream()
    stderr = FakeStream()

    console = Console(
        color=False,
        cls=False,
        stdout=stdout,
        stderr=stderr,
    )

    console.info("normal")
    console.error("failure")

    assert "normal" in stdout.getvalue()
    assert "failure" not in stdout.getvalue()

    assert "failure" in stderr.getvalue()
    assert "normal" not in stderr.getvalue()