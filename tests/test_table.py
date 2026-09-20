# tests/test_table.py

import io

import pytest

from vanta import Table


# ---------------------------------------------------------------------------
# Constructor
# ---------------------------------------------------------------------------


def test_table_requires_at_least_one_column():
    with pytest.raises(ValueError, match="at least one column"):
        Table()


def test_table_rejects_empty_column_name():
    with pytest.raises(ValueError, match="Column names cannot be empty"):
        Table("Name", "")


def test_table_rejects_whitespace_column_name():
    with pytest.raises(ValueError, match="Column names cannot be empty"):
        Table("Name", "   ")


def test_table_stores_columns():
    table = Table("Name", "Age", "Status")

    assert table.columns == ("Name", "Age", "Status")


# ---------------------------------------------------------------------------
# Rows
# ---------------------------------------------------------------------------


def test_add_row():
    table = Table("Name", "Age")

    table.add_row("Alice", 17)

    assert table.rows == (("Alice", "17"),)


def test_add_row_stringifies_values():
    table = Table("Name", "Age", "Value")

    table.add_row("Alice", 17, 3.14)

    assert table.rows == (("Alice", "17", "3.14"),)


def test_add_row_converts_none_to_empty_string():
    table = Table("Name", "Value")

    table.add_row("Alice", None)

    assert table.rows == (("Alice", ""),)


def test_add_row_requires_correct_number_of_values():
    table = Table("Name", "Age")

    with pytest.raises(ValueError, match="Expected 2 values, got 1"):
        table.add_row("Alice")


def test_add_row_returns_table():
    table = Table("Name")

    result = table.add_row("Alice")

    assert result is table


def test_add_rows():
    table = Table("Name", "Age")

    table.add_rows([
        ("Alice", 17),
        ("Bob", 21),
    ])

    assert table.rows == (
        ("Alice", "17"),
        ("Bob", "21"),
    )


def test_add_rows_returns_table():
    table = Table("Name")

    result = table.add_rows([
        ("Alice",),
        ("Bob",),
    ])

    assert result is table


def test_clear_removes_rows():
    table = Table("Name")

    table.add_row("Alice")
    table.add_row("Bob")

    table.clear()

    assert table.rows == ()


def test_clear_returns_table():
    table = Table("Name")

    result = table.clear()

    assert result is table


# ---------------------------------------------------------------------------
# Alignment
# ---------------------------------------------------------------------------


def test_single_alignment_applies_to_all_columns():
    table = Table(
        "Name",
        "Age",
        align="right",
    )

    assert table._alignments == ("right", "right")


def test_individual_column_alignments():
    table = Table(
        "Name",
        "Age",
        "Status",
        align=("left", "center", "right"),
    )

    assert table._alignments == (
        "left",
        "center",
        "right",
    )


def test_alignment_is_case_insensitive():
    table = Table(
        "Name",
        align="RIGHT",
    )

    assert table._alignments == ("right",)


def test_alignment_count_must_match_columns():
    with pytest.raises(ValueError, match="Expected 2 alignments, got 1"):
        Table(
            "Name",
            "Age",
            align=("left",),
        )


@pytest.mark.parametrize("alignment", [
    "top",
    "bottom",
    "middle",
    "",
])
def test_invalid_alignment(alignment):
    with pytest.raises(ValueError, match="Invalid alignment"):
        Table("Name", align=alignment)


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


def test_render_empty_table():
    table = Table("Name", "Age")

    assert table.render() == (
        "┌──────┬─────┐\n"
        "│ Name │ Age │\n"
        "├──────┼─────┤\n"
        "└──────┴─────┘"
    )


def test_render_table_with_rows():
    table = Table("Name", "Age")

    table.add_row("Alice", 17)
    table.add_row("Bob", 21)

    assert table.render() == (
        "┌───────┬─────┐\n"
        "│ Name  │ Age │\n"
        "├───────┼─────┤\n"
        "│ Alice │ 17  │\n"
        "│ Bob   │ 21  │\n"
        "└───────┴─────┘"
    )


def test_render_without_border():
    table = Table(
        "Name",
        "Age",
        border=False,
    )

    table.add_row("Alice", 17)

    assert table.render() == (
        "Name   Age\n"
        "─────  ───\n"
        "Alice  17 "
    )


def test_render_without_header():
    table = Table(
        "Name",
        "Age",
        header=False,
    )

    table.add_row("Alice", 17)

    assert table.render() == (
        "┌───────┬─────┐\n"
        "│ Alice │ 17  │\n"
        "└───────┴─────┘"
    )


def test_render_without_border_or_header():
    table = Table(
        "Name",
        "Age",
        border=False,
        header=False,
    )

    table.add_row("Alice", 17)

    assert table.render() == "Alice  17 "


# ---------------------------------------------------------------------------
# Alignment rendering
# ---------------------------------------------------------------------------


def test_left_alignment():
    table = Table("Name", align="left")
    table.add_row("Bob")

    assert "│ Bob  │" in table.render()


def test_right_alignment():
    table = Table("Name", align="right")
    table.add_row("Bob")

    assert "│  Bob │" in table.render()


def test_center_alignment():
    table = Table("Name", align="center")
    table.add_row("Bob")

    assert "│ Bob  │" in table.render()

def test_mixed_alignments():
    table = Table(
        "Left",
        "Center",
        "Right",
        align=("left", "center", "right"),
    )

    table.add_row("A", "B", "C")

    rendered = table.render()

    assert "A" in rendered
    assert "B" in rendered
    assert "C" in rendered


# ---------------------------------------------------------------------------
# String conversion
# ---------------------------------------------------------------------------


def test_str_returns_rendered_table():
    table = Table("Name")

    table.add_row("Alice")

    assert str(table) == table.render()


def test_print_table():
    table = Table("Name", "Age")
    table.add_row("Alice", 17)

    output = io.StringIO()

    table.print(file=output)

    assert output.getvalue() == table.render() + "\n"


# ---------------------------------------------------------------------------
# Chaining
# ---------------------------------------------------------------------------


def test_methods_can_be_chained():
    table = (
        Table("Name", "Age")
        .add_row("Alice", 17)
        .add_row("Bob", 21)
        .clear()
        .add_row("Charlie", 30)
    )

    assert table.rows == (
        ("Charlie", "30"),
    )