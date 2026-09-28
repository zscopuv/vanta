from __future__ import annotations

from datetime import datetime

from vanta.time import Time


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------


def test_time_uses_default_format() -> None:
    time = Time()

    assert time.format == "%H:%M:%S"


def test_time_accepts_custom_format() -> None:
    time = Time("%H:%M")

    assert time.format == "%H:%M"


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def test_time_renders_current_time() -> None:
    time = Time()

    expected = datetime.now().strftime("%H:%M:%S")

    assert time.render() == expected


def test_time_renders_custom_format() -> None:
    time = Time("%Y-%m-%d")

    expected = datetime.now().strftime("%Y-%m-%d")

    assert time.render() == expected


def test_time_str_returns_rendered_time() -> None:
    time = Time("%H:%M")

    assert str(time) == time.render()


def test_time_refresh_returns_current_time() -> None:
    time = Time("%H:%M:%S")

    expected = datetime.now().strftime("%H:%M:%S")

    assert time.refresh() == expected


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------


def test_time_supports_f_string_formatting() -> None:
    time = Time("%H:%M")

    assert f"{time}" == str(time)


def test_time_supports_format_spec() -> None:
    time = Time("%H:%M")

    assert format(time, ">10") == format(str(time), ">10")


# ---------------------------------------------------------------------------
# Representation
# ---------------------------------------------------------------------------


def test_time_repr() -> None:
    time = Time("%Y-%m-%d")

    assert repr(time) == "Time('%Y-%m-%d')"


def test_time_repr_with_default_format() -> None:
    time = Time()

    assert repr(time) == "Time('%H:%M:%S')"


# ---------------------------------------------------------------------------
# Common formats
# ---------------------------------------------------------------------------


def test_time_supports_date_format() -> None:
    time = Time("%Y-%m-%d")

    value = str(time)

    assert len(value) == 10
    assert value[4] == "-"
    assert value[7] == "-"


def test_time_supports_full_datetime_format() -> None:
    time = Time("%Y-%m-%d %H:%M:%S")

    value = str(time)

    assert len(value) == 19
    assert value[4] == "-"
    assert value[7] == "-"
    assert value[10] == " "
    assert value[13] == ":"
    assert value[16] == ":"


def test_time_supports_literal_text() -> None:
    time = Time("Time: %H:%M")

    value = str(time)

    assert value.startswith("Time: ")
    assert len(value) == 11


# ---------------------------------------------------------------------------
# Format consistency
# ---------------------------------------------------------------------------


def test_refresh_uses_configured_format() -> None:
    time = Time("Year: %Y")

    assert time.refresh().startswith("Year: ")


def test_render_and_refresh_use_same_format() -> None:
    time = Time("%Y-%m-%d")

    assert time.render() == time.refresh()