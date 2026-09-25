from vanta import Console

console = Console()

path = console.path(
    "Config file:",
    exists=True,
    file=True,
)

console.success(f"Using config: {path}")