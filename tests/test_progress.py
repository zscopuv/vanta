from __future__ import annotations

import io

import pytest

from vanta import Progress


def test_progress_initial_state() -> None:
    progress = Progress(100)

    assert progress.total == 100
    assert progress.current == 0
    assert progress.percentage == 0.0
    assert progress.remaining == 100
    assert progress.finished is False
    assert progress.running is False
    assert progress.completed is False


def test_progress_start() -> None:
    output = io.StringIO()
    progress = Progress(100, file=output)

    progress.start()

    assert progress.running is True
    assert progress.finished is False
    assert progress.elapsed >= 0
    assert output.getvalue()


def test_progress_update() -> None:
    output = io.StringIO()
    progress = Progress(100, file=output)

    progress.update(20)

    assert progress.current == 20
    assert progress.percentage == 20.0
    assert progress.remaining == 80
    assert progress.finished is False
    assert progress.running is True


def test_progress_update_defaults_to_one() -> None:
    progress = Progress(10, interactive=False)

    progress.update()

    assert progress.current == 1


def test_progress_finishes_at_total() -> None:
    output = io.StringIO()
    progress = Progress(10, file=output)

    progress.update(10)

    assert progress.current == 10
    assert progress.percentage == 100.0
    assert progress.remaining == 0
    assert progress.finished is True
    assert progress.completed is True
    assert progress.running is False


def test_progress_does_not_exceed_total() -> None:
    progress = Progress(10, interactive=False)

    progress.update(20)

    assert progress.current == 10
    assert progress.finished is True


def test_progress_finish() -> None:
    output = io.StringIO()
    progress = Progress(100, file=output)

    progress.start()
    progress.finish()

    assert progress.current == 100
    assert progress.finished is True
    assert progress.completed is True
    assert progress.running is False
    assert output.getvalue().endswith("\n")


def test_progress_finished_is_read_only() -> None:
    progress = Progress(10, interactive=False)

    with pytest.raises(AttributeError):
        progress.finished = True  # type: ignore[misc]


def test_progress_rejects_invalid_total() -> None:
    with pytest.raises(ValueError, match="greater than zero"):
        Progress(0)

    with pytest.raises(ValueError, match="greater than zero"):
        Progress(-1)


def test_progress_rejects_invalid_width() -> None:
    with pytest.raises(ValueError, match="greater than zero"):
        Progress(10, width=0)

    with pytest.raises(ValueError, match="greater than zero"):
        Progress(10, width=-1)


def test_progress_rejects_negative_update() -> None:
    progress = Progress(10, interactive=False)

    with pytest.raises(
        ValueError,
        match="cannot be negative",
    ):
        progress.update(-1)


def test_progress_noninteractive_produces_no_output() -> None:
    output = io.StringIO()
    progress = Progress(
        10,
        interactive=False,
        file=output,
    )

    progress.update(5)
    progress.finish()

    assert output.getvalue() == ""


def test_progress_reset() -> None:
    progress = Progress(10, interactive=False)

    progress.update(10)

    assert progress.finished is True

    progress.reset()

    assert progress.current == 0
    assert progress.percentage == 0.0
    assert progress.remaining == 10
    assert progress.finished is False
    assert progress.running is False
    assert progress.completed is False


def test_progress_context_manager() -> None:
    output = io.StringIO()

    with Progress(10, file=output) as progress:
        progress.update(5)

        assert progress.finished is False

    assert progress.finished is True
    assert progress.current == 10
    assert output.getvalue().endswith("\n")


def test_progress_renders_single_line() -> None:
    output = io.StringIO()
    progress = Progress(
        100,
        label="Working",
        file=output,
    )

    progress.update(20)
    progress.update(20)
    progress.update(20)

    value = output.getvalue()

    assert "\n" not in value
    assert "\r" in value
    assert "\033[2K" in value


def test_progress_render_contains_label_and_values() -> None:
    output = io.StringIO()
    progress = Progress(
        100,
        label="Working",
        file=output,
    )

    progress.update(20)

    value = output.getvalue()

    assert "Working" in value
    assert "20.00%" in value
    assert "(20/100)" in value


def test_progress_elapsed_is_zero_before_start() -> None:
    progress = Progress(10, interactive=False)

    assert progress.elapsed == 0.0


def test_progress_elapsed_increases_after_start() -> None:
    progress = Progress(10, interactive=False)

    progress.start()

    assert progress.elapsed >= 0.0