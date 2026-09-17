![vanta](https://i.ibb.co/q3HFNJV1/image.jpg)

# Vanta
A lightweight Python toolkit for clean, structured CLI output.

Vanta provides a simple `Console` class with:

- Colored messages
- Timestamps
- Log levels
- stdout/stderr separation
- Typed input and confirmations
- Exception handling
- Cross-platform terminal clearing
- Automatic color detection
- Interactive and non-interactive support

## Installation

```bash
pip install vanta
````

Then:

```python
import vanta

console = vanta.Console()
```

## Quick Start

```python
console.info("Hello, world!")
console.success("Operation completed.")
console.warning("Something might be wrong.")
console.error("Something went wrong.")
console.notice("Please take note.")
```

Output:

```text
[16:42:10] [INFO] Hello, world!
[16:42:10] [SUCCESS] Operation completed.
[16:42:10] [WARNING] Something might be wrong.
[16:42:10] [ERROR] Something went wrong.
[16:42:10] [NOTICE] Please take note.
```

Colors are automatically enabled when supported.

## Console

```python
console = vanta.Console()
```

Common options:

```python
console = vanta.Console(
    color=False,
    cls=True,
    level="info",
)
```

| Option        | Default      | Description                            |
| ------------- | ------------ | -------------------------------------- |
| `color`       | `None`       | Enable, disable, or auto-detect colors |
| `cls`         | `False`      | Clear the terminal on startup          |
| `interactive` | `None`       | Enable or disable interactive input    |
| `level`       | `"info"`     | Minimum log level                      |
| `stdout`      | `sys.stdout` | Normal output stream                   |
| `stderr`      | `sys.stderr` | Warning/error stream                   |

## Logging

Vanta supports seven message levels:

```python
console.debug("Debug information.")
console.info("Information.")
console.notice("Take note.")
console.success("Operation completed.")
console.warning("Something may be wrong.")
console.error("Something went wrong.")
console.critical("Critical failure.")
```

> Warnings, errors, and critical messages are written to `stderr`.

### Log Levels

Messages can be filtered:

```python
console = vanta.Console(level="warning")
```

Only `warning`, `error`, and `critical` messages will be displayed.

Available levels:

```text
debug
info
notice
success
warning
error
critical
```

## Raw Output

Use `raw()` for output without a message variant:

```python
console.raw("Hello!")
```

By default, it includes a timestamp.

```python
console.raw("Hello!", timestamp=False)
```

```text
Hello!
```

## User Input

`ask()` converts input using any callable:

```python
name = console.ask("Name:")
age = console.ask("Age:", int)
price = console.ask("Price:", float)
```

Custom validation works too:

```python
def parse_name(value: str) -> str:
    value = value.strip()

    if not value:
        raise ValueError

    return value.title()


name = console.ask("Name:", parse_name)
```

Retries can be configured:

```python
age = console.ask(
    "Age:",
    int,
    retry=3,
)
```

Use `retry=None` for unlimited retries.

## Confirmation

Use `confirm()` for yes/no prompts:

```python
if console.confirm("Continue?"):
    print("Continuing...")
```

The default is `True`:

```text
Continue? [Y/n]
```

To default to `False`:

```python
console.confirm(
    "Delete this file?",
    default=False,
)
```

Custom aliases are supported:

```python
console.confirm(
    "Continue?",
    alias_yes={"sure"},
    alias_no={"cancel"},
)
```

## Exceptions

Display exceptions easily:

```python
try:
    1 / 0
except Exception as exc:
    console.exception(exc)
```

For a full traceback:

```python
console.exception(
    exc,
    traceback=True,
)
```

## Terminal

Clear the terminal:

```python
console.clear()
```

Vanta handles Windows, Linux, and macOS automatically.

The detected terminal width is available through:

```python
console.width
```

## Colors

Colors are automatically detected.

Disable them explicitly:

```python
console = vanta.Console(color=False)
```

Vanta also respects:

```bash
NO_COLOR=1 vanta
```

and:

```bash
FORCE_COLOR=1 vanta
```

## Non-Interactive Mode

Vanta can be used without interactive input:

```python
console = vanta.Console(
    interactive=False,
)
```

This is useful for scripts, CI, and automated environments.

## API

### `Console`

```python
Console(
    color: bool | None = None,
    cls: bool = False,
    *,
    stream=None,
    stdout=None,
    stderr=None,
    input_fn=input,
    interactive: bool | None = None,
    level: str = "info",
)
```

### Messages

```python
console.debug(message)
console.info(message)
console.notice(message)
console.success(message)
console.warning(message)
console.error(message)
console.critical(message)
```

### Other

```python
console.raw(message, timestamp=True)
console.clear()
console.exception(exc, traceback=False, prefix=None)
console.ask(...)
console.confirm(...)
```

## Version

> **0.2.0 - Console & CLI Improvements**

Vanta is currently in early development. The API may change before `1.0.0`.

## License

See `LICENSE` for license information.