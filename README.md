![vanta](https://i.ibb.co/q3HFNJV1/image.jpg)

# Vanta

A lightweight Python toolkit for clean, structured CLI output.

- Colored messages
- Timestamps & log levels
- Input & confirmations
- Exception handling
- Terminal utilities
- Automatic color detection
- Interactive / non-interactive mode
- Simple terminal tables

## Installation

```bash
pip install vanta
````

## Quick Start

```python
import vanta

console = vanta.Console()

console.info("Hello, World!")

table = vanta.Table("Name", "Age", "Status")
table.add_row("Alice", 17, "Online")
table.print()
```

# Console
```python
console = vanta.Console(
    color=None,        # Auto-detect colors
    cls=False,         # Don't clear the terminal on startup
    *,
    stdout=None,       # Output stream for normal messages
    stderr=None,       # Output stream for warnings/errors
    interactive=None,  # Auto-detect interactive mode
    level="info",      # Minimum log level
)
```

## Options

| Option        | Description                       |
| ------------- | --------------------------------- |
| `color`       | Enable/disable colors             |
| `cls`         | Clear terminal on startup         |
| `stdout`      | Output stream for normal messages |
| `stderr`      | Output stream for warnings/errors |
| `interactive` | Enable/disable input              |
| `level`       | Minimum log level                 |

## Log Levels

Vanta provides 7 log levels:

| Level      | Value | Stream | Purpose                            |
| ---------- | ----: | ------ | ---------------------------------- |
| `debug`    |    10 | stdout | Detailed debugging information     |
| `info`     |    20 | stdout | General information                |
| `notice`   |    25 | stdout | Important information worth noting |
| `success`  |    30 | stdout | Successful operation               |
| `warning`  |    40 | stderr | Something may be wrong             |
| `error`    |    50 | stderr | An operation failed                |
| `critical` |    60 | stderr | Serious/critical failure           |

---

> **Lower levels are more verbose.**

> `Console.debug()` messages **won't** be shown if `level="info"` set!

## Examples

### Logging

```python
console.debug("Debug")
console.info("Info")
console.notice("Notice")
console.success("Success")
console.warning("Warning")
console.error("Error")
console.critical("Critical")
```

---

**Set a minimum log level:**

```python
console = vanta.Console(level="warning")
```

For example, `level="warning"` only emits `warning`, `error`, and `critical` messages.

---

### Input

```python
name = console.ask("Name:")
age = console.ask("Age:", int)

if console.confirm("Continue?"):
    print("Continuing!")
```

`ask()` supports custom converters and retries.

---

### Exceptions

```python
try:
    1 / 0
except Exception as exc:
    console.exception(exc)
```

Use `traceback=True` for the full traceback.

---

### Terminal

```python
console.clear()

print(console.width)
```

Vanta works on Windows, Linux, and macOS.

Colors can also be controlled with `NO_COLOR` and `FORCE_COLOR`.

## Methods

```python
console.debug(...)
console.info(...)
console.notice(...)
console.success(...)
console.warning(...)
console.error(...)
console.critical(...)

console.raw(...)
console.ask(...)
console.confirm(...)
console.exception(...)
console.clear(...)
```

# Tables
```python
table = vanta.Table(
    "Name",        # Column 1
    "Age",         # Column 2
    "Status",      # Column 3
    ...,
    align="left",  # Align cell text to the left
    border=True,   # Show table and cell borders
    header=True,   # Include column headers
)
```

## Options

| Option   | Description                 |
| -------- | --------------------------- |
| `align`  | Align cell text             |
| `border` | Show table and cell borders |
| `header` | Include column headers      |

`align` can be `left`, `center`, or `right`.

---

## Examples

```python
table = vanta.Table("Name", "Age", "Status")

table.add_row("Alice", 17, "Online")
table.add_row("Bob", 21, "Offline")

table.print()
```

---

Output:

```text
┌───────┬─────┬─────────┐
│ Name  │ Age │ Status  │
├───────┼─────┼─────────┤
│ Alice │ 17  │ Online  │
│ Bob   │ 21  │ Offline │
└───────┴─────┴─────────┘
```

## Methods

```python
table.add_row(...)
table.add_rows(...)
table.clear()
table.render()      # Returns the table as a string
table.print()       # Renders and prints the table
```

# Version

**0.3.0**

Vanta is currently in early development and the API may change before `1.0.0`.

# License

See [`LICENSE`](LICENSE).