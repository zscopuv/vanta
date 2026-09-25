"""Tests for Vanta Panel."""

from io import StringIO

import pytest

from vanta import Panel


def test_basic_panel():
    panel = Panel("Hello")

    assert str(panel) == (
        "╭───────╮\n"
        "│ Hello │\n"
        "╰───────╯"
    )


def test_multiple_content_lines():
    panel = Panel(
        "Starting server...",
        "Loading configuration...",
        "Server ready.",
    )

    lines = str(panel).splitlines()

    assert len(lines) == 5

    # Top and bottom borders.
    assert lines[0].startswith("╭")
    assert lines[0].endswith("╮")
    assert lines[4].startswith("╰")
    assert lines[4].endswith("╯")

    # Content.
    assert lines[1].strip("│ ") == "Starting server..."
    assert lines[2].strip("│ ") == "Loading configuration..."
    assert lines[3].strip("│ ") == "Server ready."

    # Every rendered line has the same width.
    assert len(lines[0]) == len(lines[1])
    assert len(lines[1]) == len(lines[2])
    assert len(lines[2]) == len(lines[3])
    assert len(lines[3]) == len(lines[4])


def test_panel_with_title():
    panel = Panel(
        "Database connected",
        title="Status",
    )

    assert str(panel) == (
        "╭────── Status ──────╮\n"
        "│ Database connected │\n"
        "╰────────────────────╯"
    )


def test_panel_without_border():
    panel = Panel(
        "Hello",
        "World",
        border=False,
    )

    assert str(panel) == (
        " Hello\n"
        " World"
    )


def test_panel_padding():
    panel = Panel(
        "Hello",
        padding=2,
    )

    assert str(panel) == (
        "╭─────────╮\n"
        "│  Hello  │\n"
        "╰─────────╯"
    )


def test_panel_custom_width():
    panel = Panel(
        "Hello",
        width=20,
    )

    lines = str(panel).splitlines()

    assert len(lines) == 3
    assert len(lines[0]) == 20
    assert len(lines[1]) == 20
    assert len(lines[2]) == 20


def test_panel_expands_when_content_is_wider_than_width():
    panel = Panel(
        "This content is wider than the requested width",
        width=10,
    )

    lines = str(panel).splitlines()

    assert len(lines) == 3
    assert len(lines[0]) > 10
    assert len(lines[1]) > 10
    assert len(lines[2]) > 10


def test_panel_content_property():
    panel = Panel("Hello", "World")

    assert panel.content == ("Hello", "World")


def test_panel_title_property():
    panel = Panel("Hello", title="Status")

    assert panel.title == "Status"


def test_panel_width_property():
    panel = Panel("Hello", width=20)

    assert panel.width == 20


def test_panel_padding_property():
    panel = Panel("Hello", padding=2)

    assert panel.padding == 2


def test_panel_border_property():
    panel = Panel("Hello", border=False)

    assert panel.border is False


def test_set_content():
    panel = Panel("Before")

    result = panel.set_content(
        "After",
        "Finished",
    )

    assert result is panel
    assert panel.content == ("After", "Finished")


def test_set_title():
    panel = Panel("Hello", title="Before")

    result = panel.set_title("After")

    assert result is panel
    assert panel.title == "After"


def test_set_title_none():
    panel = Panel("Hello", title="Status")

    panel.set_title(None)

    assert panel.title is None


def test_set_content_chaining():
    panel = Panel("Hello")

    result = (
        panel
        .set_content("Ready")
        .set_title("Status")
    )

    assert result is panel
    assert panel.content == ("Ready",)
    assert panel.title == "Status"


def test_render_returns_string():
    panel = Panel("Hello")

    result = panel.render()

    assert isinstance(result, str)
    assert result == str(panel)


def test_print():
    panel = Panel("Hello")
    output = StringIO()

    panel.print(file=output)

    assert output.getvalue() == (
        "╭───────╮\n"
        "│ Hello │\n"
        "╰───────╯\n"
    )


def test_empty_panel():
    panel = Panel()

    assert str(panel) == (
        "╭──╮\n"
        "│  │\n"
        "╰──╯"
    )


def test_non_string_content():
    panel = Panel(
        123,
        True,
        None,
    )

    assert panel.content == (
        "123",
        "True",
        "None",
    )


def test_invalid_width():
    with pytest.raises(
        ValueError,
        match="Width must be at least 1",
    ):
        Panel("Hello", width=0)


def test_negative_width():
    with pytest.raises(
        ValueError,
        match="Width must be at least 1",
    ):
        Panel("Hello", width=-1)


def test_negative_padding():
    with pytest.raises(
        ValueError,
        match="Padding cannot be negative",
    ):
        Panel("Hello", padding=-1)


def test_title_is_stringified():
    panel = Panel("Hello", title=123)

    assert panel.title == "123"


def test_content_is_stringified():
    panel = Panel(123, True, None)

    assert panel.content == (
        "123",
        "True",
        "None",
    )


def test_border_is_converted_to_bool():
    panel = Panel("Hello", border=0)

    assert panel.border is False


def test_padding_is_preserved():
    panel = Panel("Hello", padding=3)

    assert panel.padding == 3


def test_multiline_content_as_single_argument():
    panel = Panel("Hello\nWorld")

    assert panel.content == ("Hello\nWorld",)

    rendered = panel.render()

    assert "Hello\nWorld" in rendered