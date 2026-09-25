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
- Elapsed time measurement
- Timer pause and resume
- Simple terminal panels

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

> Lower levels are more verbose.

- *`level="info"`* suppresses `debug` messages
- *`level="warning"`* only emits `warning`, `error`, and `critical`

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

**Set a minimum log level:**

```python
console = vanta.Console(level="warning")
```

For example, `level="warning"` only emits `warning`, `error`, and `critical` messages.

### Input

```python
name = console.ask("Name:")
age = console.ask("Age:", int)

if console.confirm("Continue?"):
    print("Continuing!")
```

`ask()` supports custom converters and retries.

### Exceptions

```python
try:
    1 / 0
except Exception as exc:
    console.exception(exc)
```

Use `traceback=True` for the full traceback.

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

## Examples

```python
table = vanta.Table("Name", "Age", "Status")

table.add_row("Alice", 17, "Online")
table.add_row("Bob", 21, "Offline")

table.print()
```

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
# Panels
```python
panel = vanta.Panel(
    "Hello",    # 1st line
    "World",    # 2nd line
    ...
    title=None,
    width=None,
    padding=1,
    border=True,
)
```
`Panel` accepts one or more content values. Each value is rendered as a separate line.

## Options

| Option    | Description                                |
| --------- | ------------------------------------------ |
| `content` | One or more lines displayed in the panel   |
| `title`   | Optional title displayed on the top edge   |
| `width`   | Panel width; expands when content is wider |
| `padding` | Horizontal content padding                 |
| `border`  | Show or hide the panel border              |

## Examples

### Basic

```python
panel = vanta.Panel(
    "Starting server...",
    "Loading configuration...",
    "Server ready.",
    title="Status",
)

panel.print()
```

Output:

```text
╭───────── Status ──────────╮
│ Starting server...        │
│ Loading configuration...  │
│ Server ready.             │
╰───────────────────────────╯
```

### Custom Width

```python
panel = vanta.Panel(
    "Hello, World!",
    width=40,
)

panel.print()
```

The panel automatically expands if its content requires more space.

### Padding

```python
panel = vanta.Panel(
    "Hello, World!",
    padding=2,
)
```

### Without a Border

```python
panel = vanta.Panel(
    "Hello, World!",
    border=False,
)

panel.print()
```

Output:

```text
  Hello, World!
```

## Updating a Panel

```python
panel = vanta.Panel(
    "Starting...",
    title="Status",
)

panel.set_content("Finished!")
panel.set_title("Complete")

panel.print()
```

Both methods return the panel, so they can be chained:

```python
panel.set_title("Status").set_content("Ready")
```

## Properties

```python
panel.content
panel.title
panel.width
panel.padding
panel.border
```

## Methods

```python
panel.set_content(...)
panel.set_title(...)
panel.render()       # Returns the panel as a string
panel.print()        # Renders and prints the panel
```

# Progress

```python
progress = vanta.Progress(
    100,
    label="Downloading",
    width=30,
    interactive=True,
)
```

`Progress` renders a single updating progress bar in the terminal.

## Options

| Option        | Description                        |
| ------------- | ---------------------------------- |
| `total`       | Total number of steps              |
| `label`       | Text displayed before the bar      |
| `width`       | Width of the progress bar          |
| `interactive` | Enable/disable terminal rendering  |
| `file`        | Output stream for the progress bar |

## Examples

### Basic

```python
import time
import vanta

progress = vanta.Progress(100, label="Downloading")

while not progress.finished:
    time.sleep(0.02)
    progress.update()
```

Output:

```text
Downloading [██████████████████████████████] 100.00% (100/100) 2.0s
```

The progress bar updates in place rather than printing a new line for every update.

### Custom Updates

```python
progress = vanta.Progress(100, label="Processing")

while not progress.finished:
    do_some_work()
    progress.update(5)
```

Progress is automatically capped at `total`.

### Context Manager

```python
with vanta.Progress(100, label="Downloading") as progress:
    while not progress.finished:
        do_some_work()
        progress.update()
```

### Manual Finish

```python
progress = vanta.Progress(100, label="Working")

progress.start()

# Do some work...

progress.finish()
```

## Properties

| Property     | Description                               |
| ------------ | ----------------------------------------- |
| `total`      | Total number of steps                     |
| `current`    | Current progress                          |
| `percentage` | Progress as a percentage                  |
| `remaining`  | Number of remaining steps                 |
| `finished`   | Whether the progress has finished         |
| `completed`  | Whether the total has been reached        |
| `running`    | Whether the progress is currently running |
| `elapsed`    | Elapsed time in seconds                   |

## Methods

```python
progress.start()
progress.update()
progress.update(5)
progress.finish()
progress.reset()
```


# Timer
```python
timer = vanta.Timer(
    autostart=False,  # Don't start the timer immediately
)
```

## Options

| Option      | Description                 |
| ----------- | --------------------------- |
| `autostart` | Start the timer immediately |

## Examples

### Basic

```python
import time
import vanta

timer = vanta.Timer(autostart=True)

time.sleep(1.5)

timer.stop()

print(timer.elapsed)
print(timer.ms)
```

### Pause

```python
from time import sleep

from vanta import Timer


timer = Timer(autostart=True)

sleep(1.525)

timer.stop()  # Optional, but recommended

print(timer.elapsed)  # Around 1.525 sec
print(timer.ms)       # Around 1525 ms
```

Paused time is not included in the elapsed time.

### Context Manager

```python
with vanta.Timer() as timer:
    time.sleep(2)

print(timer.elapsed)
```

## Properties

| Property     | Description                         |
| ------------ | ----------------------------------- |
| `elapsed`    | Elapsed active time in seconds      |
| `ms`         | Elapsed active time in milliseconds |
| `running`    | Whether the timer is running        |
| `paused`     | Whether the timer is paused         |
| `start_time` | Time when the timer was started     |
| `stop_time`  | Time when the timer was stopped     |

## Methods

```python
timer.start()
timer.stop()
timer.pause()
timer.unpause()
timer.reset()   # Clears the timer and returns it to its initial state. Does not restart.
```

# Version

**0.4.0**

# License

See [`LICENSE`](https://github.com/zscopuv/vanta/tree/main?tab=License-1-ov-file).